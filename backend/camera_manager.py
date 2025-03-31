import cv2
import logging
import time

logger = logging.getLogger(__name__)

class CameraManager:
    def __init__(self):
        self.camera = None
        self.is_monitoring = False
        self.last_frame_time = time.time()
        self.frame_timeout = 5.0

    def initialize_camera(self):
        """初始化摄像头"""
        try:
            if self.camera is None or not self.camera.isOpened():
                for device_id in range(2):  # 尝试前两个摄像头设备
                    logger.info(f"尝试打开摄像头 {device_id}")
                    cap = cv2.VideoCapture(device_id)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret:
                            logger.info(f"成功打开摄像头 {device_id}，图像大小: {frame.shape}")
                            if self.camera is not None:
                                self.camera.release()
                            self.camera = cap
                            self.is_monitoring = True
                            return True
                        cap.release()
                    logger.warning(f"摄像头 {device_id} 打开失败")
                logger.error("所有摄像头都无法打开")
                return False
            self.is_monitoring = True
            return True
        except Exception as e:
            logger.error(f"初始化摄像头时发生错误: {e}")
            return False

    def read_frame(self):
        """读取一帧图像"""
        if not self.camera or not self.camera.isOpened():
            return None

        success, frame = self.camera.read()
        if not success:
            return None

        self.last_frame_time = time.time()
        return frame

    def release(self):
        """释放摄像头资源"""
        try:
            if self.camera is not None:
                self.camera.release()
                self.camera = None
            self.is_monitoring = False
        except Exception as e:
            logger.error(f"释放摄像头资源时发生错误: {e}")

    def is_camera_ready(self):
        """检查摄像头是否就绪"""
        return (self.camera is not None and 
                self.camera.isOpened() and 
                time.time() - self.last_frame_time < self.frame_timeout) 