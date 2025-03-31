from flask import Flask, Response, jsonify
import cv2
import mediapipe as mp
from mtcnn import MTCNN
from deepface import DeepFace
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许所有跨域请求


# 初始化 MediaPipe 姿势检测
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# 初始化 MTCNN（用于人脸检测）
detector = MTCNN()

# 打开摄像头
cap = cv2.VideoCapture(0)

# 记录夜起次数
night_wake_count = 0
# 记录当前情绪
current_emotion = None
# 记录上一次检测时间
last_detection_time = time.time()
# 情绪检测时间间隔（秒）
detection_interval = 5
# 最大情绪记录数量
max_log_size = 10
emotion_log = []


def generate_frames():
    """实时生成视频流"""
    global night_wake_count, current_emotion, last_detection_time

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()

        # **夜起检测逻辑**
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            all_out_of_bed = True

            for idx, landmark in enumerate(landmarks):
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])

                if 0 <= x < frame.shape[1] and 0 <= y < frame.shape[0]:
                    all_out_of_bed = False
                    cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
                    cv2.putText(frame, str(idx), (x, y + 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                else:
                    x_out = min(max(x, 0), frame.shape[1] - 1)
                    y_out = min(max(y, 0), frame.shape[0] - 1)
                    cv2.circle(frame, (x_out, y_out), 5, (255, 0, 0), -1)

            # **如果所有关键点都在画面外，判断为夜起**
            if all_out_of_bed:
                night_wake_count += 1
                print(f"检测到夜起，当前夜起次数: {night_wake_count}")

        # **情绪识别逻辑**
        if current_time - last_detection_time >= detection_interval:
            faces = detector.detect_faces(frame)
            if faces:
                x, y, w, h = faces[0]['box']
                face_roi = frame[y:y + h, x:x + w]
                try:
                    result = DeepFace.analyze(face_roi, actions=['emotion'])
                    current_emotion = result[0]['dominant_emotion']
                    timestamp = time.strftime('%H:%M:%S', time.localtime())
                    emotion_log.append((current_emotion, timestamp))
                    if len(emotion_log) > max_log_size:
                        emotion_log.pop(0)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, current_emotion, (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                except Exception as e:
                    print(f"情绪识别出错: {e}")

            last_detection_time = current_time

        # **维持 MJPEG 视频流**
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """提供 MJPEG 视频流"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/getData', methods=['GET'])
def get_data():
    """提供 JSON 数据：夜起次数 + 当前情绪"""
    return jsonify({
        "currentEmotion": current_emotion,
        "nightWakeCount": night_wake_count,
        "timestamp": time.strftime('%H:%M:%S', time.localtime())
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

