from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import time
from datetime import datetime
import cv2
import numpy as np
import mediapipe as mp
from mtcnn import MTCNN
from deepface import DeepFace
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from threading import Lock
from auth import db, User, SleepRecord, token_required
from posture_analyzer import PostureAnalyzer
from video_processor import CameraManager
import logging

@dataclass
class EmotionData:
    current: str
    history: List[Tuple[str, str]]
    last_update: float

@dataclass
class PostureData:
    current: str
    history: List[Tuple[str, str]]
    statistics: Dict[str, float]
    last_change: float

class DetectionState:
    def __init__(self):
        self.person_state = "IN"
        self.state_change_time = time.time()
        self.night_wake_count = 0
        self.emotion_data = EmotionData("未检测", [], time.time())
        self.posture_data = PostureData(
            "未检测",
            [],
            {
                '左侧睡': 0,
                '右侧睡': 0,
                '正常仰睡': 0,
                '左偏头仰睡': 0,
                '右偏头仰睡': 0
            },
            time.time()
        )
        self.lock = Lock()
        self.is_camera_ready = False
        self.user_id: Optional[int] = None
        self.sleep_start_time: Optional[datetime] = None
        self.sleep_end_time: Optional[datetime] = None
        self.features = {
            'posture': True,
            'emotion': True,
            'wake': True
        }

    def update_posture(self, posture: str) -> None:
        if not self.features['posture']:
            return
            
        with self.lock:
            current_time = time.time()
            if posture != self.posture_data.current:
                if self.posture_data.current in self.posture_data.statistics:
                    duration = current_time - self.posture_data.last_change
                    self.posture_data.statistics[self.posture_data.current] += duration
                
                self.posture_data.current = posture
                self.posture_data.last_change = current_time
                timestamp = time.strftime('%H:%M:%S', time.localtime())
                self.posture_data.history.append((posture, timestamp))
                if len(self.posture_data.history) > 100:
                    self.posture_data.history.pop(0)

    def update_emotion(self, emotion: str) -> None:
        with self.lock:
            self.emotion_data.current = emotion
            timestamp = time.strftime('%H:%M:%S', time.localtime())
            if not self.emotion_data.history or self.emotion_data.history[-1][0] != emotion:
                self.emotion_data.history.append((emotion, timestamp))
                if len(self.emotion_data.history) > 10:
                    self.emotion_data.history.pop(0)

    def update_night_wake(self) -> None:
        if not self.features['wake']:
            return
            
        with self.lock:
            self.night_wake_count += 1

    def get_state(self) -> Dict:
        with self.lock:
            return {
                "currentEmotion": self.emotion_data.current,
                "nightWakeCount": self.night_wake_count,
                "timestamp": time.strftime('%H:%M:%S', time.localtime()),
                "cameraStatus": "正常" if self.is_camera_ready else "未就绪",
                "userId": self.user_id,
                "sleepStartTime": self.sleep_start_time,
                "sleepEndTime": self.sleep_end_time,
                "currentPosture": self.posture_data.current
            }

class Detector(ABC):
    @abstractmethod
    def detect(self, frame: np.ndarray) -> Dict:
        pass

class EmotionDetector(Detector):
    def __init__(self, state: DetectionState):
        self.detector = MTCNN()
        self.state = state
        self.lock = Lock()
        self.target_size = (48, 48)  # DeepFace 期望的输入大小
        
    def detect(self, frame: np.ndarray) -> Dict:
        try:
            with self.lock:
                faces = self.detector.detect_faces(frame)
                if len(faces) > 0:
                    x, y, w, h = faces[0]['box']
                    x = max(0, min(x, frame.shape[1] - 1))
                    y = max(0, min(y, frame.shape[0] - 1))
                    w = min(w, frame.shape[1] - x)
                    h = min(h, frame.shape[0] - y)
                    
                    # 确保 ROI 是正方形
                    size = min(w, h)
                    x_center = x + w // 2
                    y_center = y + h // 2
                    x = x_center - size // 2
                    y = y_center - size // 2
                    
                    # 确保坐标不超出图像边界
                    x = max(0, min(x, frame.shape[1] - size))
                    y = max(0, min(y, frame.shape[0] - size))
                    
                    face_roi = frame[y:y + size, x:x + size]
                    
                    # 调整大小到目标尺寸
                    face_roi = cv2.resize(face_roi, self.target_size)
                    
                    # 确保图像是 RGB 格式
                    if len(face_roi.shape) == 2:
                        face_roi = cv2.cvtColor(face_roi, cv2.COLOR_GRAY2RGB)
                    elif face_roi.shape[2] == 4:
                        face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGRA2RGB)
                    else:
                        face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
                    
                    result = DeepFace.analyze(face_roi, actions=['emotion'])
                    
                    if result and len(result) > 0:
                        emotion = result[0]['dominant_emotion']
                        self.state.update_emotion(emotion)
                        cv2.rectangle(frame, (x, y), (x + size, y + size), (0, 255, 0), 2)
                        cv2.putText(frame, emotion, (x, y - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        return {
                            'type': 'emotion',
                            'emotion': emotion,
                            'frame': frame
                        }
                else:
                    self.state.update_emotion("未检测到人脸")
        except Exception as e:
            logger.error(f"情绪检测失败: {str(e)}")
            self.state.update_emotion("检测失败")
        return None

class PostureDetector(Detector):
    def __init__(self, state: DetectionState):
        self.analyzer = PostureAnalyzer()
        self.state = state
        self.mp_pose = mp.solutions.pose
        self.landmarks_buffer = []  # 用于存储最近的关键点坐标
        self.landmarks_buffer_size = 8  # 坐标平滑缓冲区大小
        self.smooth_factor = 0.7  # 平滑因子
        
    def smooth_landmarks(self, landmarks):
        """平滑关键点坐标"""
        if not landmarks:
            return None
            
        # 将landmarks转换为numpy数组便于计算
        current_landmarks = []
        for landmark in landmarks:
            current_landmarks.append([landmark.x, landmark.y, landmark.z])
        current_landmarks = np.array(current_landmarks)
        
        # 添加到缓冲区
        self.landmarks_buffer.append(current_landmarks)
        if len(self.landmarks_buffer) > self.landmarks_buffer_size:
            self.landmarks_buffer.pop(0)
            
        # 如果缓冲区为空，直接返回当前坐标
        if len(self.landmarks_buffer) == 0:
            return landmarks
            
        # 计算加权平均（给最近的帧更高的权重）
        weights = np.exp(np.linspace(-self.smooth_factor, 0, len(self.landmarks_buffer)))
        weights = weights / np.sum(weights)
        
        smoothed_landmarks = np.zeros_like(current_landmarks)
        for i, weight in enumerate(weights):
            smoothed_landmarks += self.landmarks_buffer[i] * weight
            
        # 将平滑后的坐标转换回landmarks格式
        for i, landmark in enumerate(landmarks):
            landmark.x = float(smoothed_landmarks[i][0])
            landmark.y = float(smoothed_landmarks[i][1])
            landmark.z = float(smoothed_landmarks[i][2])
            
        return landmarks

    def classify_posture(self, landmarks):
        """根据关键点位置分类姿势"""
        if not landmarks:
            return "未检测"
            
        try:
            # 获取关键点坐标
            left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                           landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                            landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            left_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            right_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            left_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            right_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
            left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                       landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            right_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                        landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            nose = [landmarks[self.mp_pose.PoseLandmark.NOSE.value].x,
                   landmarks[self.mp_pose.PoseLandmark.NOSE.value].y]
            
            # 转换为numpy数组进行计算
            shoulder_mid = (np.array(left_shoulder) + np.array(right_shoulder)) / 2
            hip_mid = (np.array(left_hip) + np.array(right_hip)) / 2
            
            # 计算躯干向量
            spine_vector = hip_mid - shoulder_mid
            
            # 计算躯干中点
            spine_mid = (shoulder_mid + hip_mid) / 2
            
            # 使用手腕坐标和肩部中点计算手臂向量
            left_arm_vector = np.array(left_wrist) - shoulder_mid
            right_arm_vector = np.array(right_wrist) - shoulder_mid
            
            # 计算手臂向量与躯干向量的叉积
            left_cross = np.cross(left_arm_vector, spine_vector)
            right_cross = np.cross(right_arm_vector, spine_vector)
            
            # 计算头部姿势
            nose_vec = np.array(nose) - shoulder_mid
            dot_nose = np.dot(nose_vec, spine_vector)
            angle_nose = np.arccos(dot_nose / (np.linalg.norm(nose_vec) * np.linalg.norm(spine_vector))) * 180/np.pi
            cross_nose = np.cross(nose_vec, spine_vector)
            
            # 1. 首先判断手部是否在同一侧（侧睡判断）
            if (left_cross > 0 and right_cross > 0) or (left_cross < 0 and right_cross < 0):
                # 计算双手的平均向量
                avg_hand_vec = (left_arm_vector + right_arm_vector) / 2
                dot_product = np.dot(avg_hand_vec, spine_vector)
                angle = np.arccos(dot_product / (np.linalg.norm(avg_hand_vec) * np.linalg.norm(spine_vector) + 1e-6)) * 180/np.pi
                
                cross_product = np.cross(avg_hand_vec, spine_vector)
                if cross_product > 0:
                    return "左侧睡" if angle < 180 else "右侧睡"
                else:
                    return "右侧睡" if angle < 180 else "左侧睡"
            
            # 2. 如果手臂关键点检测不到或者手臂向量太小，使用躯干中点判断
            if np.linalg.norm(left_arm_vector) < 0.05 or np.linalg.norm(right_arm_vector) < 0.05:
                # 如果双手叉积同号（都在左侧或都在右侧），则判定为侧睡
                if (left_cross > 0 and right_cross > 0) or (left_cross < 0 and right_cross < 0):
                    if left_cross < 0:  # 如果叉积为负，说明在左侧
                        return "左侧睡"
                    else:  # 如果叉积为正，说明在右侧
                        return "右侧睡"
            
            # 3. 如果不是侧睡，则判断仰卧位相关姿势
            # 根据叉积和角度综合判断头部偏转方向
            if cross_nose > 0:
                if angle_nose > 10:
                    return "左偏头仰睡"
                else:
                    return "正常仰睡"
            else:
                if angle_nose > 10:
                    return "右偏头仰睡"
                else:
                    return "正常仰睡"
                    
        except Exception as e:
            print(f"姿势分类错误: {e}")
            return "未检测"
        
    def detect(self, frame: np.ndarray) -> Dict:
        if not self.state.features['posture']:
            return None
            
        try:
            # 处理帧并获取关键点
            processed_frame = self.analyzer.process_frame(frame)
            results = self.analyzer.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            if not results.pose_landmarks:
                return {
                    'type': 'posture',
                    'posture': '未检测',
                    'landmarks': None,
                    'frame': processed_frame
                }
            
            # 平滑关键点坐标
            smoothed_landmarks = self.smooth_landmarks(results.pose_landmarks.landmark)
            
            # 分类姿势
            current_posture = self.classify_posture(smoothed_landmarks)
            
            # 更新状态
            if current_posture != self.state.posture_data.current:
                self.state.update_posture(current_posture)
            
            # 检查人员是否在画面中
            in_frame = smoothed_landmarks is not None
            current_time = time.time()
            
            if in_frame and self.state.person_state == "OUT":
                if current_time - self.state.state_change_time >= 1.0:
                    self.state.person_state = "IN"
                    self.state.update_night_wake()
            elif not in_frame and self.state.person_state == "IN":
                self.state.state_change_time = current_time
                self.state.person_state = "OUT"
            
            # 转换关键点数据为前端需要的格式
            landmarks_data = []
            if smoothed_landmarks:
                for landmark in smoothed_landmarks:
                    landmarks_data.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z
                    })
            
            return {
                'type': 'posture',
                'posture': current_posture,
                'landmarks': landmarks_data,
                'frame': processed_frame
            }
            
        except Exception as e:
            print(f"姿势检测错误: {e}")
            return None

app = Flask(__name__)
CORS(app)

state = DetectionState()
camera = CameraManager()

camera.detection_pipeline.add_detector(EmotionDetector(state))
camera.detection_pipeline.add_detector(PostureDetector(state))

def generate_frames():
    while True:
        try:
            if not camera.is_monitoring:
                break

            frame = camera.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            results = camera.get_results()
            if results:
                for result in results['results']:
                    if result and result['type'] == 'posture':
                        frame = result['frame']
                    elif result and result['type'] == 'emotion':
                        frame = result['frame']

            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret:
                continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except Exception:
            time.sleep(0.1)

@app.route('/video_feed')
def video_feed():
    if not camera.is_ready():
        return "Camera not available", 503
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/getData', methods=['GET'])
def get_data():
    return jsonify(state.get_state())

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "camera_status": "正常" if camera.is_available() else "未就绪",
        "timestamp": time.strftime('%H:%M:%S', time.localtime())
    })

@app.route('/start_monitoring')
def start_monitoring():
    try:
        if not camera.start():
            return jsonify({'error': '无法初始化摄像头'}), 503
        
        # 重置所有状态
        state.posture_data.current = '未检测'
        state.emotion_data.current = '未检测'
        state.night_wake_count = 0
        state.person_state = "OUT"  # 重置人员状态
        state.state_change_time = time.time()  # 重置状态改变时间
        state.posture_data.statistics = {
            '左侧睡': 0,
            '右侧睡': 0,
            '正常仰睡': 0,
            '左偏头仰睡': 0,
            '右偏头仰睡': 0
        }
        state.posture_data.history = []
        state.emotion_data.history = []
        state.posture_data.last_change = time.time()
        
        # 启用必要的功能
        state.features['posture'] = True
        state.features['wake'] = True
        state.features['emotion'] = True
        
        return jsonify({'message': '监测已开始'})
    except Exception as e:
        logger.error(f"启动监测失败: {e}")
        return jsonify({'error': '启动监测失败'}), 500

@app.route('/stop_monitoring')
def stop_monitoring():
    try:
        camera.stop()
        return jsonify({'message': '监测已停止'})
    except Exception:
        return jsonify({'error': '停止监测失败'}), 500

@app.route('/get_monitoring_data')
def get_monitoring_data():
    try:
        with state.lock:
            current_time = time.time()
            if state.posture_data.current in state.posture_data.statistics:
                current_duration = current_time - state.posture_data.last_change
                state.posture_data.statistics[state.posture_data.current] += current_duration
            
            return jsonify({
                'posture': {
                    'current': state.posture_data.current,
                    'statistics': state.posture_data.statistics
                },
                'emotion': {
                    'current': state.emotion_data.current,
                    'history': state.emotion_data.history
                },
                'wake': {
                    'count': state.night_wake_count
                }
            })
    except Exception:
        return jsonify({'error': '获取监测数据失败'}), 500

@app.route('/toggle_feature', methods=['POST'])
def toggle_feature():
    try:
        data = request.get_json()
        feature = data.get('feature')
        enabled = data.get('enabled', False)
        
        if feature not in state.features:
            return jsonify({'error': '无效的功能名称'}), 400
            
        state.features[feature] = enabled
        
        return jsonify({
            'message': f"功能 {feature} 已{'启用' if enabled else '禁用'}",
            'features': state.features
        })
    except Exception:
        return jsonify({'error': '切换功能失败'}), 500

@app.route('/get_features', methods=['GET'])
def get_features():
    return jsonify(state.features)

if __name__ == '__main__':
    try:
        app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
    finally:
        camera.stop()