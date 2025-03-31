from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
import cv2
import numpy as np
import mediapipe as mp
import time
from threading import Lock
from collections import defaultdict

@dataclass
class PostureData:
    current: str
    landmarks: Optional[List[List[float]]]
    position_description: str
    history: List[Dict]
    stats: Dict[str, Dict[str, float]]
    last_change: float

class PostureDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.camera: Optional[cv2.VideoCapture] = None
        self.is_monitoring = False
        self.lock = Lock()
        self.posture_data = PostureData(
            current="未检测",
            landmarks=None,
            position_description="未检测到人体",
            history=[],
            stats=defaultdict(lambda: {"count": 0, "total_duration": 0}),
            last_change=time.time()
        )

    def classify_posture(self, landmarks: List[List[float]]) -> str:
        """根据关键点位置分类姿势"""
        if not landmarks or len(landmarks) < 25:
            return "未检测到人体"
        
        try:
            # 获取关键点索引
            left_shoulder = 11
            right_shoulder = 12
            left_hip = 23
            right_hip = 24
            nose = 0
            
            # 计算关键向量
            shoulder_midpoint = (np.array(landmarks[left_shoulder]) + np.array(landmarks[right_shoulder])) / 2
            hip_midpoint = (np.array(landmarks[left_hip]) + np.array(landmarks[right_hip])) / 2
            spine_vector = hip_midpoint - shoulder_midpoint
            
            # 计算身体朝向角度
            lateral_angle = np.degrees(np.arctan2(spine_vector[0], spine_vector[1]))
            
            # 根据角度判断姿势
            if lateral_angle > 20:
                return "左侧睡"
            elif lateral_angle < -20:
                return "右侧睡"
            else:
                # 判断头部位置
                nose_offset = landmarks[nose][0] - shoulder_midpoint[0]
                
                if nose_offset > 0.1:
                    return "左偏头仰睡"
                elif nose_offset < -0.1:
                    return "右偏头仰睡"
                else:
                    return "正常仰睡"
                    
        except Exception:
            return "姿势识别错误"

    def update_posture_history(self, new_posture: str) -> None:
        """更新姿势历史记录"""
        with self.lock:
            if new_posture != self.posture_data.current:
                if self.posture_data.current != "未检测到人体":
                    duration = time.time() - self.posture_data.last_change
                    self.posture_data.stats[self.posture_data.current]["count"] += 1
                    self.posture_data.stats[self.posture_data.current]["total_duration"] += duration
                    
                    self.posture_data.history.append({
                        "posture": self.posture_data.current,
                        "duration": int(duration),
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                
                self.posture_data.current = new_posture
                self.posture_data.last_change = time.time()

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """处理单帧图像"""
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(frame_rgb)
            
            if results.pose_landmarks:
                landmarks = []
                for landmark in results.pose_landmarks.landmark:
                    landmarks.append([landmark.x, landmark.y, landmark.z])
                
                posture = self.classify_posture(landmarks)
                self.update_posture_history(posture)
                
                self.posture_data.current = posture
                self.posture_data.landmarks = landmarks
                self.posture_data.position_description = f"检测到{posture}姿势"
                
                # 绘制关键点和姿势文本
                mp_drawing = mp.solutions.drawing_utils
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                cv2.putText(frame, f"姿势: {posture}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                self.posture_data.current = "未检测到人体"
                self.posture_data.landmarks = None
                self.posture_data.position_description = "未检测到人体"
                cv2.putText(frame, "未检测到人体", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
        except Exception:
            self.posture_data.current = "处理错误"
            self.posture_data.landmarks = None
            self.posture_data.position_description = "处理图像时出错"
            cv2.putText(frame, "处理错误", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        return frame

    def generate_frames(self):
        """生成视频流"""
        while self.is_monitoring:
            success, frame = self.camera.read()
            if not success:
                continue
            
            processed_frame = self.process_frame(frame)
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            if not ret:
                continue
                
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    def start_monitoring(self) -> bool:
        """开始监测"""
        try:
            with self.lock:
                if self.is_monitoring:
                    return True
                
                self.camera = cv2.VideoCapture(0)
                if not self.camera.isOpened():
                    return False
                
                self.is_monitoring = True
                self.posture_data.history = []
                self.posture_data.stats = defaultdict(lambda: {"count": 0, "total_duration": 0})
                return True
        except Exception:
            self.stop_monitoring()
            return False

    def stop_monitoring(self) -> None:
        """停止监测"""
        with self.lock:
            self.is_monitoring = False
            self.posture_data.current = "未检测"
            self.posture_data.landmarks = None
            self.posture_data.position_description = "未检测到人体"
            
            if self.camera and self.camera.isOpened():
                self.camera.release()
                self.camera = None

    def get_monitoring_data(self) -> Dict:
        """获取监测数据"""
        with self.lock:
            return {
                "posture": {
                    "current": self.posture_data.current,
                    "position_description": self.posture_data.position_description,
                    "landmarks": self.posture_data.landmarks
                },
                "history": self.posture_data.history[-10:] if self.posture_data.history else []
            }

# Flask应用初始化
app = Flask(__name__)
CORS(app)
detector = PostureDetector()

@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "camera_status": "正常" if detector.camera and detector.camera.isOpened() else "未就绪",
        "timestamp": time.strftime('%H:%M:%S', time.localtime())
    })

@app.route('/start_monitoring')
def start_monitoring():
    """开始监测接口"""
    if detector.start_monitoring():
        return jsonify({"message": "监测已开始"})
    return jsonify({"error": "启动监测失败"}), 500

@app.route('/stop_monitoring')
def stop_monitoring():
    """停止监测接口"""
    detector.stop_monitoring()
    return jsonify({"message": "监测已停止"})

@app.route('/get_monitoring_data')
def get_monitoring_data():
    """获取监测数据接口"""
    if not detector.is_monitoring:
        return jsonify({"error": "Monitoring not started"}), 503
    return jsonify(detector.get_monitoring_data())

@app.route('/video_feed')
def video_feed():
    """视频流接口"""
    if not detector.is_monitoring or not detector.camera or not detector.camera.isOpened():
        return jsonify({"error": "Camera not available"}), 503
    return Response(detector.generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)