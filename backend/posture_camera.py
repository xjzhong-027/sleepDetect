import cv2
import mediapipe as mp
import numpy as np
from threading import Thread, Lock
import time
from datetime import datetime

class PostureCamera:
    def __init__(self):
        self.camera = None
        self.is_running = False
        self.frame = None
        self.frame_lock = Lock()
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3,
            model_complexity=0
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # 添加帧率控制
        self.fps = 30
        self.frame_interval = 1.0 / self.fps
        self.last_frame_time = 0
        
        # 姿势检测相关变量
        self.current_posture = "未检测"
        self.posture_start_time = None
        self.posture_history = []
        self.posture_lock = Lock()
        
        # 姿势稳定性相关变量
        self.posture_buffer = []  # 用于存储最近的姿势检测结果
        self.buffer_size = 5      # 缓冲区大小
        self.last_update_time = 0 # 上次更新时间
        self.update_interval = 1.0 # 更新间隔（秒）
        
        # 添加坐标平滑相关变量
        self.landmarks_buffer = []  # 用于存储最近的关键点坐标
        self.landmarks_buffer_size = 8  # 增加坐标平滑缓冲区大小
        self.smooth_factor = 0.7  # 增加平滑因子，以减少抖动
        
        # 手腕坐标历史记录（用于进一步平滑手腕位置）
        self.left_wrist_history = []
        self.right_wrist_history = []
        self.wrist_history_size = 10  # 手腕历史记录大小
        
        # 姿势说明字典
        self.posture_descriptions = {
            "左侧睡": {
                "description": "身体向左侧倾斜，肩部和髋部呈一定角度。",
                "suggestion": "此姿势有助于缓解胃酸反流，但需注意左肩和左臂的压力。建议使用合适的枕头支撑头部。",
                "health_impact": "优点：缓解胃酸反流\n缺点：可能压迫左肩和左臂"
            },
            "右侧睡": {
                "description": "身体向右侧倾斜，肩部和髋部保持对齐。",
                "suggestion": "适合孕妇睡眠，但需注意右肩和右臂的血液循环。建议使用孕妇专用枕头。",
                "health_impact": "优点：适合孕妇\n缺点：可能影响右肩血液循环"
            },
            "正常仰睡": {
                "description": "身体平躺，脊椎自然伸展，头部与床面平行。",
                "suggestion": "有助于维持脊椎自然曲线，但可能加重打鼾情况。建议使用适当高度的枕头。",
                "health_impact": "优点：保护脊椎\n缺点：可能加重打鼾"
            },
            "左偏头仰睡": {
                "description": "仰卧位基础上头部向左偏转。",
                "suggestion": "注意颈部肌肉的拉伸程度，避免长期保持以防颈部疲劳。建议调整枕头位置。",
                "health_impact": "优点：缓解颈部压力\n缺点：可能导致颈部肌肉疲劳"
            },
            "右偏头仰睡": {
                "description": "仰卧位基础上头部向右偏转。",
                "suggestion": "需注意颈椎的扭转角度，建议使用合适高度的枕头辅助。",
                "health_impact": "优点：缓解颈部压力\n缺点：可能导致颈椎不适"
            }
        }

        # 添加床的参考点
        self.bed_reference_points = {
            'head': None,  # 床头位置
            'foot': None,  # 床尾位置
            'left': None,  # 床左侧位置
            'right': None  # 床右侧位置
        }
        
        # 添加坐标转换参数
        self.coordinate_transform = {
            'scale': 1.0,  # 缩放因子
            'offset_x': 0,  # X轴偏移
            'offset_y': 0,  # Y轴偏移
            'offset_z': 0   # Z轴偏移
        }

    def calculate_angle(self, a, b, c):
        """计算三个点形成的角度"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360-angle
            
        return angle

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
            
            # 获取关键点置信度
            left_wrist_confidence = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].visibility
            right_wrist_confidence = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].visibility
            
            # 平滑手腕坐标（额外的平滑处理）
            # 1. 添加到历史记录
            self.left_wrist_history.append(np.array(left_wrist))
            self.right_wrist_history.append(np.array(right_wrist))
            
            # 2. 保持历史记录大小
            if len(self.left_wrist_history) > self.wrist_history_size:
                self.left_wrist_history.pop(0)
            if len(self.right_wrist_history) > self.wrist_history_size:
                self.right_wrist_history.pop(0)
            
            # 3. 计算加权平均
            if len(self.left_wrist_history) > 1:
                weights = np.exp(np.linspace(-1.0, 0, len(self.left_wrist_history)))
                weights = weights / np.sum(weights)
                
                left_wrist_smoothed = np.zeros(2)
                right_wrist_smoothed = np.zeros(2)
                
                for i, weight in enumerate(weights):
                    left_wrist_smoothed += self.left_wrist_history[i] * weight
                    right_wrist_smoothed += self.right_wrist_history[i] * weight
                
                # 根据置信度决定是否使用平滑后的坐标
                if left_wrist_confidence > 0.5:  # 只有当置信度足够高才使用平滑后的坐标
                    left_wrist = left_wrist_smoothed
                else:
                    # 如果置信度低，则使用肘部位置作为替代
                    left_wrist = np.array(left_elbow)
                    
                if right_wrist_confidence > 0.5:
                    right_wrist = right_wrist_smoothed
                else:
                    right_wrist = np.array(right_elbow)
            
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
                    return "右侧睡" if angle < 180 else "左侧睡"  # 镜像反转
                else:
                    return "左侧睡" if angle < 180 else "右侧睡"  # 镜像反转
            
            # 2. 如果手臂关键点检测不到或者手臂向量太小，使用躯干中点判断
            if np.linalg.norm(left_arm_vector) < 0.05 or np.linalg.norm(right_arm_vector) < 0.05:
                # 如果双手叉积同号（都在左侧或都在右侧），则判定为侧睡
                if (left_cross > 0 and right_cross > 0) or (left_cross < 0 and right_cross < 0):
                    if left_cross < 0:  # 如果叉积为负，说明在左侧
                        return "右侧睡"  # 镜像反转
                    else:  # 如果叉积为正，说明在右侧
                        return "左侧睡"  # 镜像反转
            
            # 3. 如果不是侧睡，则判断仰卧位相关姿势
            # 根据叉积和角度综合判断头部偏转方向
            if cross_nose > 0:
                if angle_nose > 10:
                    return "右偏头仰睡"  # 镜像反转
                else:
                    return "正常仰睡"
            else:
                if angle_nose > 10:
                    return "左偏头仰睡"  # 镜像反转
                else:
                    return "正常仰睡"
                    
        except Exception as e:
            print(f"姿势分类错误: {e}")
            return "未检测"

    def get_stable_posture(self, posture):
        """获取稳定的姿势判断结果"""
        current_time = time.time()
        
        # 添加新的姿势到缓冲区
        self.posture_buffer.append(posture)
        if len(self.posture_buffer) > self.buffer_size:
            self.posture_buffer.pop(0)
        
        # 检查是否需要更新
        if current_time - self.last_update_time < self.update_interval:
            return self.current_posture
        
        # 统计缓冲区中最常见的姿势
        posture_counts = {}
        for p in self.posture_buffer:
            posture_counts[p] = posture_counts.get(p, 0) + 1
        
        # 找出最常见的姿势
        stable_posture = max(posture_counts.items(), key=lambda x: x[1])[0]
        
        # 只有当姿势发生变化时才更新
        if stable_posture != self.current_posture:
            self.last_update_time = current_time
            return stable_posture
        
        return self.current_posture

    def update_posture_history(self, posture):
        """更新姿势历史记录"""
        current_time = datetime.now()
        
        with self.posture_lock:
            # 如果姿势发生变化，记录之前的姿势
            if posture != self.current_posture:
                if self.posture_start_time:
                    duration = (current_time - self.posture_start_time).total_seconds()
                    # 只有当持续时间超过0.5秒时才记录
                    if duration >= 0.5:
                        self.posture_history.append({
                            "posture": self.current_posture,
                            "duration": duration,
                            "timestamp": self.posture_start_time.strftime("%H:%M:%S")
                        })
                
                self.current_posture = posture
                self.posture_start_time = current_time
            
            # 每2秒记录一次当前姿势
            if self.posture_start_time:
                elapsed = (current_time - self.posture_start_time).total_seconds()
                if elapsed >= 2.0:  # 每2秒记录一次
                    self.posture_history.append({
                        "posture": self.current_posture,
                        "duration": 2.0,
                        "timestamp": current_time.strftime("%H:%M:%S")
                    })
                    self.posture_start_time = current_time

    def start_camera(self):
        try:
            # 如果摄像头已经在运行，先停止它
            if self.camera is not None:
                self.stop_camera()
                time.sleep(0.2)  # 等待资源释放
            
            # 重新初始化摄像头
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                raise Exception("无法打开摄像头")
            
            # 设置摄像头参数
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # 重置所有状态
            self.is_running = True
            self.frame = None
            self.last_frame_time = 0
            self.current_posture = "未检测"
            self.posture_start_time = None
            self.posture_history = []
            self.posture_buffer = []
            
            # 启动捕获线程
            Thread(target=self._capture_loop, daemon=True).start()
            return True
        except Exception as e:
            print(f"启动摄像头时发生错误: {e}")
            return False

    def stop_camera(self):
        try:
            self.is_running = False
            # 等待捕获线程结束
            time.sleep(0.1)
            
            with self.frame_lock:
                self.frame = None
            
            if self.camera is not None:
                self.camera.release()
                self.camera = None
            
            # 重置所有状态
            self.current_posture = "未检测"
            self.posture_start_time = None
            self.posture_history = []
            self.posture_buffer = []
            self.last_frame_time = 0
            
            return True
        except Exception as e:
            print(f"停止摄像头时发生错误: {e}")
            return False

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
            # 给手腕关键点额外的平滑
            if i == self.mp_pose.PoseLandmark.LEFT_WRIST.value or i == self.mp_pose.PoseLandmark.RIGHT_WRIST.value:
                # 手腕使用更强的平滑
                landmark.x = float(smoothed_landmarks[i][0])
                landmark.y = float(smoothed_landmarks[i][1])
                landmark.z = float(smoothed_landmarks[i][2])
            else:
                # 其他关键点使用普通平滑
                landmark.x = float(smoothed_landmarks[i][0])
                landmark.y = float(smoothed_landmarks[i][1])
                landmark.z = float(smoothed_landmarks[i][2])
            
        return landmarks

    def _draw_landmarks(self, frame, landmarks, h, w):
        """绘制关键点和连接线"""
        try:
            # 1. 躯干关键点
            left_shoulder = [int(landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w),
                           int(landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h)]
            right_shoulder = [int(landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * w),
                            int(landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * h)]
            left_hip = [int(landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x * w),
                      int(landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y * h)]
            right_hip = [int(landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x * w),
                       int(landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y * h)]
            
            # 2. 手臂关键点
            left_elbow = [int(landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x * w),
                        int(landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y * h)]
            right_elbow = [int(landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x * w),
                         int(landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y * h)]
            left_wrist = [int(landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x * w),
                        int(landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y * h)]
            right_wrist = [int(landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x * w),
                         int(landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y * h)]
            
            # 3. 头部关键点
            nose = [int(landmarks[self.mp_pose.PoseLandmark.NOSE.value].x * w),
                   int(landmarks[self.mp_pose.PoseLandmark.NOSE.value].y * h)]
            neck = [int(landmarks[self.mp_pose.PoseLandmark.NOSE.value].x * w),
                   int(landmarks[self.mp_pose.PoseLandmark.NOSE.value].y * h)]
            
            # 计算中点
            shoulder_mid = [(left_shoulder[0] + right_shoulder[0]) // 2,
                          (left_shoulder[1] + right_shoulder[1]) // 2]
            hip_mid = [(left_hip[0] + right_hip[0]) // 2,
                      (left_hip[1] + right_hip[1]) // 2]
            
            # 定义颜色
            TORSO_COLOR = (255, 255, 255)      # 绿色 - 躯干
            ARMS_COLOR = (255, 255, 255)     # 橙色 - 手臂
            HEAD_COLOR = (255, 255, 255)     # 紫色 - 头部
            POINT_COLOR = (0, 0, 255)      # 红色 - 关键点
            
            # 绘制躯干连线（绿色）
            cv2.line(frame, shoulder_mid, hip_mid, TORSO_COLOR, 2)  # 躯干中轴线
            cv2.line(frame, left_shoulder, right_shoulder, TORSO_COLOR, 2)  # 肩部连线
            cv2.line(frame, left_hip, right_hip, TORSO_COLOR, 2)  # 髋部连线
            cv2.line(frame, left_shoulder, left_hip, TORSO_COLOR, 2)  # 左侧躯干
            cv2.line(frame, right_shoulder, right_hip, TORSO_COLOR, 2)  # 右侧躯干
            
            # 绘制手臂连线（橙色）
            cv2.line(frame, left_shoulder, left_elbow, ARMS_COLOR, 2)
            cv2.line(frame, left_elbow, left_wrist, ARMS_COLOR, 2)
            cv2.line(frame, right_shoulder, right_elbow, ARMS_COLOR, 2)
            cv2.line(frame, right_elbow, right_wrist, ARMS_COLOR, 2)
            
            # 绘制头部连线（紫色）
            cv2.line(frame, shoulder_mid, neck, HEAD_COLOR, 2)
            
            # 绘制所有关键点（红色）
            # 躯干关键点
            cv2.circle(frame, left_shoulder, 5, POINT_COLOR, -1)
            cv2.circle(frame, right_shoulder, 5, POINT_COLOR, -1)
            cv2.circle(frame, left_hip, 5, POINT_COLOR, -1)
            cv2.circle(frame, right_hip, 5, POINT_COLOR, -1)
            
            # 手臂关键点
            cv2.circle(frame, left_elbow, 5, POINT_COLOR, -1)
            cv2.circle(frame, right_elbow, 5, POINT_COLOR, -1)
            cv2.circle(frame, left_wrist, 5, POINT_COLOR, -1)
            cv2.circle(frame, right_wrist, 5, POINT_COLOR, -1)
            
            # 头部关键点
            cv2.circle(frame, nose, 5, POINT_COLOR, -1)
            cv2.circle(frame, neck, 5, POINT_COLOR, -1)
            
            # 绘制中点（红色）
            cv2.circle(frame, shoulder_mid, 5, POINT_COLOR, -1)
            cv2.circle(frame, hip_mid, 5, POINT_COLOR, -1)
            
            # 在画面上显示当前姿势（使用半透明背景）
            if self.current_posture != "未检测":
                # 创建半透明背景
                overlay = frame.copy()
                cv2.rectangle(overlay, (10, 30), (400, 80), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
                
                # 添加姿势文本
                cv2.putText(frame, self.current_posture, (20, 60),
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
        except Exception as e:
            pass  # 不输出错误信息

    def _capture_loop(self):
        last_landmarks = None
        last_posture = "未检测"
        last_update_time = 0
        update_interval = 0.5  # 每0.5秒更新一次姿势历史
        
        while self.is_running:
            try:
                current_time = time.time()
                
                # 控制帧率
                if current_time - self.last_frame_time < self.frame_interval:
                    time.sleep(0.001)
                    continue
                
                # 读取摄像头帧
                ret, frame = self.camera.read()
                if not ret:
                    time.sleep(0.1)
                    continue
                
                # 水平翻转帧
                frame = cv2.flip(frame, 1)
                
                # 转换为RGB格式
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 实时进行姿势检测
                try:
                    results = self.pose.process(rgb_frame)
                    
                    if results.pose_landmarks:
                        # 平滑关键点坐标
                        smoothed_landmarks = self.smooth_landmarks(results.pose_landmarks.landmark)
                        if smoothed_landmarks is not None:
                            # 获取关键点坐标
                            landmarks = smoothed_landmarks
                            last_landmarks = landmarks
                            
                            # 分类姿势
                            posture = self.classify_posture(landmarks)
                            
                            # 每0.5秒更新一次姿势历史
                            if current_time - last_update_time >= update_interval:
                                if posture != last_posture:
                                    self.update_posture_history(posture)
                                    last_posture = posture
                                last_update_time = current_time
                            
                            # 绘制关键点和连接线
                            h, w, _ = frame.shape
                            self._draw_landmarks(frame, landmarks, h, w)
                            
                except Exception as e:
                    pass
                
                # 更新帧
                with self.frame_lock:
                    self.frame = frame
                self.last_frame_time = current_time
                
                time.sleep(0.01)
                
            except Exception as e:
                time.sleep(0.1)

    def get_frame(self):
        with self.frame_lock:
            if self.frame is not None:
                return self.frame.copy()  # 返回帧的副本
        return None

    def is_camera_active(self):
        return self.camera is not None and self.camera.isOpened()

    def get_current_posture(self):
        """获取当前姿势信息"""
        with self.posture_lock:
            if self.current_posture in self.posture_descriptions:
                return {
                    "posture": self.current_posture,
                    "description": self.posture_descriptions[self.current_posture]["description"],
                    "suggestion": self.posture_descriptions[self.current_posture]["suggestion"],
                    "health_impact": self.posture_descriptions[self.current_posture]["health_impact"]
                }
            return {
                "posture": self.current_posture,
                "description": "等待检测人体姿势...",
                "suggestion": "",
                "health_impact": ""
            }

    def get_posture_history(self):
        """获取姿势历史记录"""
        with self.posture_lock:
            return self.posture_history.copy()

    def transform_coordinates(self, landmarks):
        """将MediaPipe坐标转换为相对于床的坐标"""
        if not landmarks or not self.bed_reference_points['head']:
            return None
            
        try:
            # 获取床的参考点
            bed_head = np.array(self.bed_reference_points['head'])
            bed_foot = np.array(self.bed_reference_points['foot'])
            bed_left = np.array(self.bed_reference_points['left'])
            bed_right = np.array(self.bed_reference_points['right'])
            
            # 计算床的方向向量
            bed_length = bed_foot - bed_head
            bed_width = bed_right - bed_left
            
            # 计算床的中心点
            bed_center = (bed_head + bed_foot) / 2
            
            # 转换关键点坐标
            transformed_landmarks = []
            for landmark in landmarks:
                # 将MediaPipe坐标转换为相对于床中心的坐标
                point = np.array([landmark[0], landmark[1], landmark[2]])
                
                # 计算相对于床中心的偏移
                relative_pos = point - bed_center
                
                # 应用坐标变换
                transformed_point = relative_pos * self.coordinate_transform['scale']
                transformed_point += np.array([
                    self.coordinate_transform['offset_x'],
                    self.coordinate_transform['offset_y'],
                    self.coordinate_transform['offset_z']
                ])
                
                transformed_landmarks.append(transformed_point.tolist())
            
            return transformed_landmarks
            
        except Exception as e:
            print(f"坐标转换错误: {e}")
            return None

    def get_current_landmarks(self):
        """获取当前关键点数据（相对于床的坐标）"""
        with self.frame_lock:
            if self.frame is None:
                return None
                
            try:
                # 获取当前帧的关键点数据
                rgb_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(rgb_frame)
                
                if not results.pose_landmarks:
                    return None
                    
                # 获取原始关键点坐标
                landmarks = []
                for landmark in results.pose_landmarks.landmark:
                    landmarks.append([
                        landmark.x,
                        landmark.y,
                        landmark.z
                    ])
                
                # 如果床的参考点未设置，直接返回原始坐标
                if not all(self.bed_reference_points.values()):
                    return landmarks
                
                # 转换为相对于床的坐标
                transformed_landmarks = self.transform_coordinates(landmarks)
                return transformed_landmarks if transformed_landmarks is not None else landmarks
                
            except Exception as e:
                print(f"获取关键点数据时发生错误: {e}")
                return None

    def update_bed_reference_points(self, points):
        """更新床的参考点"""
        self.bed_reference_points = points
        # 更新坐标转换参数
        self.update_coordinate_transform()

    def update_coordinate_transform(self):
        """更新坐标转换参数"""
        if not all(self.bed_reference_points.values()):
            return
            
        # 计算床的尺寸
        bed_length = np.linalg.norm(self.bed_reference_points['foot'] - self.bed_reference_points['head'])
        bed_width = np.linalg.norm(self.bed_reference_points['right'] - self.bed_reference_points['left'])
        
        # 根据床的尺寸调整缩放因子
        self.coordinate_transform['scale'] = 1.0 / max(bed_length, bed_width)
        
        # 设置偏移量，使坐标原点位于床的中心
        bed_center = (self.bed_reference_points['head'] + self.bed_reference_points['foot']) / 2
        self.coordinate_transform['offset_x'] = -bed_center[0]
        self.coordinate_transform['offset_y'] = -bed_center[1]
        self.coordinate_transform['offset_z'] = -bed_center[2]

# 创建全局姿势摄像头处理器实例
posture_camera = PostureCamera() 