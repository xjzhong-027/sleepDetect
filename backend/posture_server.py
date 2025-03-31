from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from posture_camera import posture_camera
import cv2
import numpy as np
import time

app = Flask(__name__)
# 配置CORS，允许所有来源的请求
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

def generate_frames():
    while True:
        try:
            # 检查摄像头状态
            if not posture_camera.is_camera_active():
                break

            # 获取帧
            frame = posture_camera.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            # 图像压缩
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret:
                continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except Exception as e:
            time.sleep(0.1)
            continue

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_monitoring')
def start_monitoring():
    try:
        if posture_camera.start_camera():
            return jsonify({"status": "success", "message": "摄像头已启动"})
        else:
            return jsonify({"status": "error", "message": "摄像头已在运行中"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/stop_monitoring')
def stop_monitoring():
    try:
        # 先停止摄像头
        if posture_camera.stop_camera():
            # 等待一小段时间确保资源释放
            time.sleep(0.2)
            return jsonify({"status": "success", "message": "摄像头已停止"})
        else:
            return jsonify({"status": "error", "message": "摄像头未在运行"})
    except Exception as e:
        print(f"停止监控时发生错误: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/check_camera')
def check_camera():
    try:
        if posture_camera.is_camera_active():
            return jsonify({"status": "success", "message": "摄像头已就绪"})
        else:
            return jsonify({"status": "error", "message": "摄像头未就绪"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "camera_status": "正常" if posture_camera.is_camera_active() else "未就绪"
    })

@app.route('/toggle_feature', methods=['POST', 'OPTIONS'])
def toggle_feature():
    if request.method == 'OPTIONS':
        # 处理预检请求
        return '', 204
    
    try:
        data = request.get_json()
        feature = data.get('feature')
        enabled = data.get('enabled')
        
        if feature == 'posture':
            # 这里可以添加姿势检测功能的开关逻辑
            return jsonify({
                "status": "success",
                "message": f"姿势检测功能已{'启用' if enabled else '禁用'}"
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"未知的功能: {feature}"
            }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/get_monitoring_data')
def get_monitoring_data():
    try:
        current_posture = posture_camera.get_current_posture()
        history = posture_camera.get_posture_history()
        landmarks = posture_camera.get_current_landmarks()
        
        response_data = {
            "status": "success",
            "posture": current_posture,
            "history": history,
            "landmarks": landmarks if landmarks is not None else []
        }
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/set_bed_reference', methods=['POST'])
def set_bed_reference():
    try:
        data = request.get_json()
        reference_points = data.get('reference_points')
        
        if not reference_points or not all(key in reference_points for key in ['head', 'foot', 'left', 'right']):
            return jsonify({
                "status": "error",
                "message": "缺少必要的参考点数据"
            }), 400
            
        # 更新床的参考点
        posture_camera.update_bed_reference_points(reference_points)
        
        return jsonify({
            "status": "success",
            "message": "床的参考点已更新"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 