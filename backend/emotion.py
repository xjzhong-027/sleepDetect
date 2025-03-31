from mtcnn import MTCNN
from deepface import DeepFace
import cv2
import time

# 创建 MTCNN 检测器
detector = MTCNN()

# 打开摄像头
cap = cv2.VideoCapture(0)

# 用于存储情绪和时间戳的列表
emotion_log = []
# 滚动轴显示的最大情绪记录数量
max_log_size = 10
# 记录上一次检测的时间
last_detection_time = time.time()
# 检测间隔时间（秒）
detection_interval = 5
# 当前检测到的情绪，初始化为 None
current_emotion = None

while True:
    # 读取摄像头的一帧图像
    ret, frame = cap.read()
    if not ret:
        break

    current_time = time.time()
    # 每 5 秒进行一次人脸检测和情绪识别
    if current_time - last_detection_time >= detection_interval:
        # 检测人脸
        faces = detector.detect_faces(frame)

        if len(faces) > 0:
            # 提取第一个检测到的人脸区域
            x, y, w, h = faces[0]['box']
            face_roi = frame[y:y + h, x:x + w]

            try:
                # 进行情绪识别
                result = DeepFace.analyze(face_roi, actions=['emotion'])
                current_emotion = result[0]['dominant_emotion']
                # 获取当前时间戳
                timestamp = time.strftime('%H:%M:%S', time.localtime())
                emotion_log.append((current_emotion, timestamp))
                # 如果记录数量超过最大数量，删除最早的记录
                if len(emotion_log) > max_log_size:
                    emotion_log.pop(0)

                print(f"识别到的情绪是: {current_emotion}，时间: {timestamp}")

                # 在图像上绘制人脸框和显示情绪
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, current_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            except Exception as e:
                print(f"情绪识别出错: {e}")
        else:
            print("未检测到人脸。")
            current_emotion = None

        last_detection_time = current_time
    else:
        if current_emotion:
            print(f"当前情绪: {current_emotion}，时间: {time.strftime('%H:%M:%S', time.localtime())}")

    # 在图像上显示情绪记录滚动轴
    y_offset = 30
    for index, (emotion, timestamp) in enumerate(reversed(emotion_log)):
        text = f"{timestamp}: {emotion}"
        cv2.putText(frame, text, (10, y_offset + index * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1)

    # 显示处理后的图像
    cv2.imshow('Face Emotion Recognition', frame)

    # 按 'q' 键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放摄像头资源并关闭所有窗口
cap.release()
cv2.destroyAllWindows()