import cv2
import mediapipe as mp
import csv
import numpy as np
import os

def process_sleep_image(image_path):
    # 创建输出CSV文件夹（如果不存在）
    csv_output_folder = 'out_csv'
    if not os.path.exists(csv_output_folder):
        os.makedirs(csv_output_folder)
    # 创建输出图片文件夹（如果不存在）
    image_output_folder = 'out_image'
    if not os.path.exists(image_output_folder):
        os.makedirs(image_output_folder)

    # 初始化MediaPipe Pose模块
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)  # 静态图片模式
    mp_drawing = mp.solutions.drawing_utils

    # 读取图片
    image = cv2.imread(image_path)

    # 提取图片文件名（不包含扩展名）
    image_name = os.path.splitext(os.path.basename(image_path))[0]

    # 生成对应的 CSV 文件名
    csv_path = os.path.join(csv_output_folder, f"{image_name}.csv")

    # 转换颜色空间 BGR -> RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 处理图像获取关键点
    results = pose.process(image_rgb)

    if results.pose_landmarks is None:
        print("未检测到人体关键点，请检查图像或调整检测参数。")
        return None

    with open(csv_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        # 写入表头
        writer.writerow(["Landmark ID", "x", "y", "z", "Visibility"])
        # 遍历所有33个关键点
        for landmark_id, landmark in enumerate(results.pose_landmarks.landmark):
            writer.writerow([
                landmark_id,
                landmark.x,        # 归一化x坐标（0-1）
                landmark.y,        # 归一化y坐标（0-1）
                landmark.z,        # 相对深度
                landmark.visibility  # 可见性置信度（0-1）
            ])

    print(f"关键点已保存至 {csv_path}")

    # 从CSV文件中读取关键点数据
    landmarks = {}
    with open(csv_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # 跳过表头
        for row in reader:
            landmark_id = int(row[0])
            x = float(row[1])
            y = float(row[2])
            landmarks[landmark_id] = np.array([x, y])  # 只取x, y坐标

    # 假设的关键点ID
    LEFT_SHOULDER_ID = 11
    RIGHT_SHOULDER_ID = 12
    LEFT_HIP_ID = 23
    RIGHT_HIP_ID = 24
    NOSE_ID = 0
    LEFT_WRIST_ID = 15
    RIGHT_WRIST_ID = 16

    # 计算两肩中点和两髋中点
    shoulder_midpoint = (landmarks[LEFT_SHOULDER_ID] + landmarks[RIGHT_SHOULDER_ID]) / 2
    hip_midpoint = (landmarks[LEFT_HIP_ID] + landmarks[RIGHT_HIP_ID]) / 2

    # 计算身体中轴向量
    spine_vector = hip_midpoint - shoulder_midpoint

    # 计算双肩连线的向量
    shoulder_vector = landmarks[RIGHT_SHOULDER_ID] - landmarks[LEFT_SHOULDER_ID]

    # 计算两髋连线的向量
    hip_vector = landmarks[RIGHT_HIP_ID] - landmarks[LEFT_HIP_ID]

    # 判断手是否在身体中轴同一侧
    left_wrist_vector = landmarks[LEFT_WRIST_ID] - shoulder_midpoint
    right_wrist_vector = landmarks[RIGHT_WRIST_ID] - shoulder_midpoint

    left_cross = np.cross(left_wrist_vector, spine_vector)
    right_cross = np.cross(right_wrist_vector, spine_vector)
    if (left_cross > 0 and right_cross > 0) or (left_cross < 0 and right_cross < 0):
        # 取平均手部向量
        avg_hand_vector = (left_wrist_vector + right_wrist_vector) / 2

        # 计算平均手部向量与身体中轴线向量的夹角
        dot_product = np.dot(avg_hand_vector, spine_vector)
        norm_avg_hand_vector = np.linalg.norm(avg_hand_vector)
        norm_spine_vector = np.linalg.norm(spine_vector)

        # 避免分母为零，添加极小常量
        epsilon = 1e-6
        norm_avg_hand_vector = max(norm_avg_hand_vector, epsilon)
        norm_spine_vector = max(norm_spine_vector, epsilon)

        angle = np.arccos(dot_product / (norm_avg_hand_vector * norm_spine_vector)) * (180 / np.pi)

        # 判断方向
        cross_product = np.cross(avg_hand_vector, spine_vector)
        if cross_product > 0:
            if angle < 180:
                sleep_position = "这个人很可能处于左侧睡姿势"
            else:
                sleep_position = "这个人很可能处于右侧睡姿势"
        else:
            if angle < 180:
                sleep_position = "这个人很可能处于右侧睡姿势"
            else:
                sleep_position = "这个人很可能处于左侧睡姿势"
    else:
        # 设定平行判断的角度阈值（单位：度）
        parallel_angle_threshold = 10

        # 使用向量夹角判断两肩和两髋连线是否平行
        dot_product = np.dot(shoulder_vector, hip_vector)
        norm_shoulder_vector = np.linalg.norm(shoulder_vector)
        norm_hip_vector = np.linalg.norm(hip_vector)

        # 避免分母为零，添加极小常量
        epsilon = 1e-6
        norm_shoulder_vector = max(norm_shoulder_vector, epsilon)
        norm_hip_vector = max(norm_hip_vector, epsilon)

        angle = np.arccos(dot_product / (norm_shoulder_vector * norm_hip_vector)) * (180 / np.pi)
        print(f"双肩连线向量与两髋连线向量的夹角为: {angle:.2f} 度")

        # 鼻尖到两肩中点的向量
        nose_to_shoulder_midpoint = landmarks[NOSE_ID] - shoulder_midpoint

        # 计算鼻尖向量与中轴向量的夹角
        dot_product_nose = np.dot(nose_to_shoulder_midpoint, spine_vector)
        norm_nose_to_shoulder_midpoint = np.linalg.norm(nose_to_shoulder_midpoint)
        norm_spine_vector = np.linalg.norm(spine_vector)

        # 避免分母为零，添加极小常量
        epsilon = 1e-6
        norm_nose_to_shoulder_midpoint = max(norm_nose_to_shoulder_midpoint, epsilon)
        norm_spine_vector = max(norm_spine_vector, epsilon)

        nose_angle = np.arccos(dot_product_nose / (norm_nose_to_shoulder_midpoint * norm_spine_vector)) * (180 / np.pi)

        # 判断鼻尖在中轴的左侧还是右侧
        cross_product = np.cross(nose_to_shoulder_midpoint, spine_vector)
        print(cross_product)
        if cross_product > 0:  # 鼻尖在中轴左侧
            if nose_angle > 10:
                sleep_position = "左偏头仰睡"
            else:
                sleep_position = "正常仰睡"
        else:  # 鼻尖在中轴右侧
            if nose_angle > 10:
                sleep_position = "右偏头仰睡"
            else:
                sleep_position = "正常仰睡"

    # 可视化（可选）
    annotated_image = image.copy()
    mp_drawing.draw_landmarks(
        annotated_image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS)

    # 获取图像的高度和宽度
    h, w, _ = annotated_image.shape

    # 绘制双肩连线的向量
    start_point = (int(landmarks[LEFT_SHOULDER_ID][0] * w), int(landmarks[LEFT_SHOULDER_ID][1] * h))
    end_point = (int((landmarks[LEFT_SHOULDER_ID][0] + shoulder_vector[0]) * w), int((landmarks[LEFT_SHOULDER_ID][1] + shoulder_vector[1]) * h))
    cv2.arrowedLine(annotated_image, start_point, end_point, (255, 0, 0), 2)  # 蓝色箭头
    # 绘制身体中轴向量
    spine_start_point = (int(shoulder_midpoint[0] * w), int(shoulder_midpoint[1] * h))
    spine_end_point = (int((shoulder_midpoint[0] + spine_vector[0]) * w), int((shoulder_midpoint[1] + spine_vector[1]) * h))
    cv2.arrowedLine(annotated_image, spine_start_point, spine_end_point, (0, 0, 255), 2)  # 红色箭头
    # 绘制两髋连线的向量
    start_point = (int(landmarks[LEFT_HIP_ID][0] * w), int(landmarks[LEFT_HIP_ID][1] * h))
    end_point = (int((landmarks[LEFT_HIP_ID][0] + hip_vector[0]) * w), int((landmarks[LEFT_HIP_ID][1] + hip_vector[1]) * h))
    cv2.arrowedLine(annotated_image, start_point, end_point, (0, 255, 0), 2)  # 绿色箭头

    # 标注角度
    text = f'Angle: {angle:.2f} degrees'
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    text_x = int((w - text_size[0]) / 2)
    text_y = int((h + text_size[1]) / 2)
    cv2.putText(annotated_image, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    # 生成输出图片的完整路径
    output_image_path = os.path.join(image_output_folder, f"{image_name}_annotated_pose_with_vectors.jpg")
    # 保存带有向量和角度标注的图像
    cv2.imwrite(output_image_path, annotated_image)

    return sleep_position, output_image_path