import cv2
import mediapipe as mp
import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PostureAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.current_posture = "未检测"
        self.current_landmarks = None

    def process_frame(self, frame):
        """处理单帧图像并分析姿势"""
        try:
            # 转换颜色空间并进行姿势检测
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(frame_rgb)

            if not results.pose_landmarks:
                self.current_posture = "未检测到人体"
                self.current_landmarks = None
                return frame

            # 提取关键点坐标
            landmarks = {}
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                # 直接存储为列表而不是 ndarray
                landmarks[str(idx)] = [landmark.x, landmark.y, landmark.z]

            # 分析姿势
            self.current_posture = self.analyze_posture(landmarks)
            self.current_landmarks = landmarks

            # 绘制关键点和连接线
            self._draw_pose_landmarks(frame, results.pose_landmarks, landmarks)

            return frame

        except Exception as e:
            logger.error(f"处理帧时发生错误: {e}")
            return frame

    def analyze_posture(self, landmarks):
        """分析姿势"""
        try:
            # 定义关键点ID
            LEFT_SHOULDER_ID = '11'
            RIGHT_SHOULDER_ID = '12'
            LEFT_HIP_ID = '23'
            RIGHT_HIP_ID = '24'
            NOSE_ID = '0'
            LEFT_WRIST_ID = '15'
            RIGHT_WRIST_ID = '16'

            # 将列表转换为 numpy 数组进行计算
            shoulder_midpoint = (np.array(landmarks[LEFT_SHOULDER_ID]) + 
                               np.array(landmarks[RIGHT_SHOULDER_ID])) / 2
            hip_midpoint = (np.array(landmarks[LEFT_HIP_ID]) + 
                          np.array(landmarks[RIGHT_HIP_ID])) / 2

            # 计算身体中轴向量
            spine_vector = hip_midpoint - shoulder_midpoint

            # 判断手是否在身体中轴同一侧
            left_wrist_vector = np.array(landmarks[LEFT_WRIST_ID]) - shoulder_midpoint
            right_wrist_vector = np.array(landmarks[RIGHT_WRIST_ID]) - shoulder_midpoint

            # 使用二维向量进行叉乘计算
            left_cross = np.cross(left_wrist_vector[:2], spine_vector[:2])
            right_cross = np.cross(right_wrist_vector[:2], spine_vector[:2])

            if (left_cross > 0 and right_cross > 0) or (left_cross < 0 and right_cross < 0):
                return self._analyze_side_posture(left_wrist_vector, right_wrist_vector, spine_vector)
            else:
                return self._analyze_supine_posture(np.array(landmarks[NOSE_ID]), 
                                                  shoulder_midpoint, 
                                                  spine_vector)

        except Exception as e:
            logger.error(f"姿势分析错误: {e}")
            return "姿势分析错误"

    def _analyze_side_posture(self, left_wrist_vector, right_wrist_vector, spine_vector):
        """分析侧卧姿势"""
        # 取平均手部向量
        avg_hand_vector = (left_wrist_vector + right_wrist_vector) / 2

        # 计算平均手部向量与身体中轴线向量的夹角
        dot_product = np.dot(avg_hand_vector[:2], spine_vector[:2])
        norm_avg_hand_vector = np.linalg.norm(avg_hand_vector[:2])
        norm_spine_vector = np.linalg.norm(spine_vector[:2])

        # 避免分母为零
        epsilon = 1e-6
        norm_avg_hand_vector = max(norm_avg_hand_vector, epsilon)
        norm_spine_vector = max(norm_spine_vector, epsilon)

        angle = np.arccos(dot_product / (norm_avg_hand_vector * norm_spine_vector)) * (180 / np.pi)
        cross_product = np.cross(avg_hand_vector[:2], spine_vector[:2])

        return "左侧睡" if cross_product > 0 else "右侧睡"

    def _analyze_supine_posture(self, nose, shoulder_midpoint, spine_vector):
        """分析仰卧姿势"""
        # 鼻尖到两肩中点的向量
        nose_to_shoulder_midpoint = nose - shoulder_midpoint

        # 计算鼻尖向量与中轴向量的夹角
        dot_product = np.dot(nose_to_shoulder_midpoint[:2], spine_vector[:2])
        norm_nose = np.linalg.norm(nose_to_shoulder_midpoint[:2])
        norm_spine = np.linalg.norm(spine_vector[:2])

        # 避免分母为零
        epsilon = 1e-6
        norm_nose = max(norm_nose, epsilon)
        norm_spine = max(norm_spine, epsilon)

        angle = np.arccos(dot_product / (norm_nose * norm_spine)) * (180 / np.pi)
        cross_product = np.cross(nose_to_shoulder_midpoint[:2], spine_vector[:2])

        if cross_product > 0:  # 鼻尖在中轴左侧
            return "左偏头仰睡" if angle > 10 else "正常仰睡"
        else:  # 鼻尖在中轴右侧
            return "右偏头仰睡" if angle > 10 else "正常仰睡"

    def _draw_pose_landmarks(self, frame, pose_landmarks, landmarks):
        """绘制姿势关键点和向量"""
        # 绘制关键点和连接线
        mp.solutions.drawing_utils.draw_landmarks(
            frame, pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

        # 添加姿势文本
        cv2.putText(frame, self.current_posture, (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 获取图像的高度和宽度
        h, w, _ = frame.shape

        # 绘制身体中轴向量
        shoulder_midpoint = (np.array(landmarks['11']) + np.array(landmarks['12'])) / 2
        hip_midpoint = (np.array(landmarks['23']) + np.array(landmarks['24'])) / 2
        spine_vector = hip_midpoint - shoulder_midpoint

        spine_start = (int(shoulder_midpoint[0] * w), int(shoulder_midpoint[1] * h))
        spine_end = (int((shoulder_midpoint[0] + spine_vector[0]) * w), 
                    int((shoulder_midpoint[1] + spine_vector[1]) * h))
        cv2.arrowedLine(frame, spine_start, spine_end, (0, 0, 255), 2)

    def get_current_state(self):
        """获取当前姿势状态"""
        return {
            "posture": self.current_posture,
            "landmarks": self.current_landmarks  # 现在 landmarks 已经是可 JSON 序列化的字典
        }

    def close(self):
        """释放资源"""
        self.pose.close() 