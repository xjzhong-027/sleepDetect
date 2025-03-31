from dataclasses import dataclass
from typing import Optional, Dict, List
import cv2
import numpy as np
import time
from queue import Queue
from threading import Thread, Event, Lock
from concurrent.futures import ThreadPoolExecutor
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class Detector(ABC):
    @abstractmethod
    def detect(self, frame: np.ndarray) -> Dict:
        pass

@dataclass
class Frame:
    data: np.ndarray
    timestamp: float

class FrameBuffer:
    def __init__(self, maxsize: int = 30):
        self.queue = Queue(maxsize=maxsize)
        self.lock = Lock()
        self.is_full = Event()
        self.is_empty = Event()
        self.is_empty.set()
        self.last_frame_time = 0
        self.frame_interval = 1.0 / 30  # 30 FPS

    def put(self, frame: Frame) -> bool:
        try:
            current_time = time.time()
            # 如果帧间隔太短，跳过这一帧
            if current_time - self.last_frame_time < self.frame_interval:
                return True
                
            self.last_frame_time = current_time
            if self.queue.full():
                # 如果队列满了，移除最旧的帧
                try:
                    self.queue.get_nowait()
                except:
                    pass
            self.queue.put(frame)
            self.is_empty.clear()
            if self.queue.full():
                self.is_full.set()
            return True
        except Exception as e:
            logger.error(f"添加帧到缓冲区失败: {e}")
            return False

    def get(self) -> Optional[Frame]:
        try:
            if self.queue.empty():
                return None
            frame = self.queue.get_nowait()
            self.is_full.clear()
            if self.queue.empty():
                self.is_empty.set()
            return frame
        except Exception as e:
            logger.error(f"从缓冲区获取帧失败: {e}")
            return None

class VideoCapture:
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.cap = None
        self.is_running = False
        self.frame_buffer = FrameBuffer()
        self.capture_thread = None
        self.fps = 30
        self.last_frame_time = 0
        self.frame_interval = 1.0 / self.fps
        self.retry_count = 0
        self.max_retries = 3

    def start(self) -> bool:
        try:
            if self.cap is not None:
                self.release()

            self.cap = cv2.VideoCapture(self.device_id)
            if not self.cap.isOpened():
                logger.error(f"无法打开摄像头 {self.device_id}")
                return False

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)

            self.is_running = True
            self.retry_count = 0
            self.capture_thread = Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            return True
        except Exception as e:
            logger.error(f"启动视频捕获失败: {e}")
            return False

    def _capture_loop(self):
        while self.is_running:
            try:
                current_time = time.time()
                if current_time - self.last_frame_time < self.frame_interval:
                    time.sleep(0.001)  # 短暂休眠以避免CPU过载
                    continue

                ret, frame = self.cap.read()
                if ret:
                    self.last_frame_time = current_time
                    self.retry_count = 0  # 重置重试计数
                    frame = cv2.resize(frame, (640, 480))
                    self.frame_buffer.put(Frame(frame, current_time))
                else:
                    self.retry_count += 1
                    if self.retry_count >= self.max_retries:
                        logger.warning("摄像头读取失败，尝试重新初始化")
                        self.cap.release()
                        self.cap = cv2.VideoCapture(self.device_id)
                        if not self.cap.isOpened():
                            logger.error("重新初始化摄像头失败")
                            time.sleep(1.0)
                            continue
                        self.retry_count = 0
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"视频捕获循环出错: {e}")
                time.sleep(0.1)

    def release(self):
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
            self.cap = None

class DetectionPipeline:
    def __init__(self, frame_buffer: FrameBuffer):
        self.frame_buffer = frame_buffer
        self.is_running = False
        self.process_thread = None
        self.detectors = []
        self.result_queue = Queue()
        self.executor = None
        self._init_executor()

    def _init_executor(self):
        if self.executor is not None:
            self.executor.shutdown(wait=False)
        self.executor = ThreadPoolExecutor(max_workers=2)

    def add_detector(self, detector):
        self.detectors.append(detector)

    def start(self):
        self.is_running = True
        self._init_executor()  # 确保线程池已初始化
        self.process_thread = Thread(target=self._process_loop, daemon=True)
        self.process_thread.start()

    def _process_loop(self):
        while self.is_running:
            try:
                frame = self.frame_buffer.get()
                if frame is None:
                    time.sleep(0.01)
                    continue

                # 使用线程池并行处理检测
                futures = []
                for detector in self.detectors:
                    future = self.executor.submit(detector.detect, frame.data)
                    futures.append(future)

                # 等待所有检测完成
                results = []
                for future in futures:
                    try:
                        result = future.result(timeout=0.1)
                        if result is not None:
                            results.append(result)
                    except Exception as e:
                        logger.error(f"检测处理失败: {e}")

                if results:
                    self.result_queue.put({
                        'timestamp': frame.timestamp,
                        'results': results
                    })

            except Exception as e:
                logger.error(f"处理循环出错: {e}")
                time.sleep(0.1)

    def stop(self):
        self.is_running = False
        if self.process_thread:
            self.process_thread.join(timeout=1.0)
        if self.executor:
            self.executor.shutdown(wait=False)
            self.executor = None

class CameraManager:
    def __init__(self):
        self.video_capture = VideoCapture()
        self.detection_pipeline = DetectionPipeline(self.video_capture.frame_buffer)
        self.is_monitoring = False
        self.lock = Lock()
        self.is_camera_ready = False

    def start(self) -> bool:
        with self.lock:
            if self.is_monitoring:
                return True

            if not self.video_capture.start():
                return False

            self.detection_pipeline.start()
            self.is_monitoring = True
            self.is_camera_ready = True
            return True

    def stop(self):
        with self.lock:
            if not self.is_monitoring:
                return

            self.detection_pipeline.stop()
            self.video_capture.release()
            self.is_monitoring = False
            self.is_camera_ready = False

    def get_frame(self) -> Optional[np.ndarray]:
        frame = self.video_capture.frame_buffer.get()
        return frame.data if frame else None

    def get_results(self) -> Optional[Dict]:
        try:
            return self.detection_pipeline.result_queue.get_nowait()
        except:
            return None

    def is_ready(self) -> bool:
        """检查摄像头是否正在监控中"""
        return self.is_monitoring and self.is_camera_ready

    def is_available(self) -> bool:
        """检查摄像头是否可用"""
        try:
            if self.video_capture.cap is None:
                self.video_capture.cap = cv2.VideoCapture(self.video_capture.device_id)
            return self.video_capture.cap is not None and self.video_capture.cap.isOpened()
        except Exception as e:
            logger.error(f"检查摄像头可用性时发生错误: {e}")
            return False 