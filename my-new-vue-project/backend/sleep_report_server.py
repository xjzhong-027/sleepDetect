from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# 创建保存报告的目录
REPORT_DIR = "sleep_reports"
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

def calculate_sleep_score(posture_data, emotion_data, wake_count, sleep_duration):
    """计算睡眠质量评分"""
    score = 100
    
    # 姿势评分（40分）
    posture_score = 40
    if posture_data.get("正常仰睡", 0) < 0.3 * sleep_duration:  # 如果正常仰睡时间少于30%
        posture_score -= 10
    if posture_data.get("左侧睡", 0) > 0.4 * sleep_duration:  # 如果左侧睡时间超过40%
        posture_score -= 10
    if posture_data.get("右侧睡", 0) > 0.4 * sleep_duration:  # 如果右侧睡时间超过40%
        posture_score -= 10
    
    # 情绪评分（30分）
    emotion_score = 30
    if emotion_data.get("angry", 0) > 0.1 * sleep_duration:  # 如果愤怒情绪超过10%
        emotion_score -= 10
    if emotion_data.get("sad", 0) > 0.2 * sleep_duration:  # 如果悲伤情绪超过20%
        emotion_score -= 10
    if emotion_data.get("fear", 0) > 0.1 * sleep_duration:  # 如果恐惧情绪超过10%
        emotion_score -= 10
    
    # 夜起评分（30分）
    wake_score = 30
    if wake_count > 3:  # 如果夜起次数超过3次
        wake_score -= 10 * (wake_count - 3)
    
    return min(100, max(0, posture_score + emotion_score + wake_score))

def generate_posture_chart(posture_data, sleep_duration):
    """生成姿势分布饼图"""
    plt.figure(figsize=(8, 6))
    postures = list(posture_data.keys())
    durations = [posture_data[p] / sleep_duration * 100 for p in postures]
    
    plt.pie(durations, labels=postures, autopct='%1.1f%%')
    plt.title('睡眠姿势分布')
    
    # 将图表转换为base64字符串
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode()

def generate_emotion_chart(emotion_data, sleep_duration):
    """生成情绪变化折线图"""
    plt.figure(figsize=(10, 6))
    emotions = list(emotion_data.keys())
    durations = [emotion_data[e] / sleep_duration * 100 for e in emotions]
    
    sns.barplot(x=emotions, y=durations)
    plt.title('睡眠情绪分布')
    plt.xlabel('情绪类型')
    plt.ylabel('持续时间 (%)')
    plt.xticks(rotation=45)
    
    # 将图表转换为base64字符串
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode()

def generate_sleep_report(posture_data, emotion_data, wake_count, sleep_duration, start_time, end_time):
    """生成睡眠报告"""
    # 计算睡眠评分
    sleep_score = calculate_sleep_score(posture_data, emotion_data, wake_count, sleep_duration)
    
    # 生成图表
    posture_chart = generate_posture_chart(posture_data, sleep_duration)
    emotion_chart = generate_emotion_chart(emotion_data, sleep_duration)
    
    # 生成报告内容
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sleep_period": {
            "start": start_time,
            "end": end_time,
            "duration": sleep_duration
        },
        "sleep_score": sleep_score,
        "posture_data": posture_data,
        "emotion_data": emotion_data,
        "wake_count": wake_count,
        "charts": {
            "posture": posture_chart,
            "emotion": emotion_chart
        },
        "analysis": {
            "posture_analysis": analyze_posture(posture_data, sleep_duration),
            "emotion_analysis": analyze_emotion(emotion_data, sleep_duration),
            "wake_analysis": analyze_wake(wake_count),
            "overall_analysis": generate_overall_analysis(sleep_score, posture_data, emotion_data, wake_count)
        }
    }
    
    return report

def analyze_posture(posture_data, sleep_duration):
    """分析姿势数据"""
    analysis = []
    
    # 分析正常仰睡时间
    normal_sleep_time = posture_data.get("正常仰睡", 0)
    if normal_sleep_time < 0.3 * sleep_duration:
        analysis.append("正常仰睡时间不足，建议适当增加仰卧时间以保护脊椎。")
    
    # 分析侧睡时间
    left_sleep_time = posture_data.get("左侧睡", 0)
    right_sleep_time = posture_data.get("右侧睡", 0)
    if left_sleep_time > 0.4 * sleep_duration:
        analysis.append("左侧睡时间过长，可能会压迫心脏和胃部，建议适当调整。")
    if right_sleep_time > 0.4 * sleep_duration:
        analysis.append("右侧睡时间过长，可能会影响右肩血液循环，建议适当调整。")
    
    return analysis

def analyze_emotion(emotion_data, sleep_duration):
    """分析情绪数据"""
    analysis = []
    
    # 分析负面情绪
    if emotion_data.get("angry", 0) > 0.1 * sleep_duration:
        analysis.append("睡眠期间出现较多愤怒情绪，建议睡前进行放松活动。")
    if emotion_data.get("sad", 0) > 0.2 * sleep_duration:
        analysis.append("睡眠期间出现较多悲伤情绪，建议保持积极心态。")
    if emotion_data.get("fear", 0) > 0.1 * sleep_duration:
        analysis.append("睡眠期间出现较多恐惧情绪，建议改善睡眠环境。")
    
    return analysis

def analyze_wake(wake_count):
    """分析夜起情况"""
    analysis = []
    
    if wake_count > 3:
        analysis.append(f"夜起次数较多（{wake_count}次），建议检查睡眠环境或身体状况。")
    elif wake_count > 0:
        analysis.append(f"夜起{wake_count}次，属于正常范围。")
    else:
        analysis.append("睡眠质量良好，没有夜起。")
    
    return analysis

def generate_overall_analysis(sleep_score, posture_data, emotion_data, wake_count):
    """生成总体分析"""
    analysis = []
    
    if sleep_score >= 90:
        analysis.append("睡眠质量优秀，继续保持良好的睡眠习惯。")
    elif sleep_score >= 80:
        analysis.append("睡眠质量良好，有少许需要改进的地方。")
    elif sleep_score >= 70:
        analysis.append("睡眠质量一般，建议关注睡眠习惯的改善。")
    else:
        analysis.append("睡眠质量需要改善，建议咨询专业医生。")
    
    return analysis

@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        data = request.get_json()
        
        # 从请求中获取数据
        posture_data = data.get('posture_data', {})
        emotion_data = data.get('emotion_data', {})
        wake_count = data.get('wake_count', 0)
        sleep_duration = data.get('sleep_duration', 0)
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        # 生成报告
        report = generate_sleep_report(
            posture_data,
            emotion_data,
            wake_count,
            sleep_duration,
            start_time,
            end_time
        )
        
        # 保存报告
        report_filename = f"sleep_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(REPORT_DIR, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            "status": "success",
            "message": "睡眠报告生成成功",
            "report": report
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/get_report/<report_id>', methods=['GET'])
def get_report(report_id):
    try:
        report_path = os.path.join(REPORT_DIR, f"sleep_report_{report_id}.json")
        
        if not os.path.exists(report_path):
            return jsonify({
                "status": "error",
                "message": "报告不存在"
            }), 404
        
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        return jsonify({
            "status": "success",
            "report": report
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/list_reports', methods=['GET'])
def list_reports():
    try:
        reports = []
        for filename in os.listdir(REPORT_DIR):
            if filename.startswith("sleep_report_") and filename.endswith(".json"):
                report_path = os.path.join(REPORT_DIR, filename)
                with open(report_path, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    reports.append({
                        "id": filename.replace("sleep_report_", "").replace(".json", ""),
                        "timestamp": report["timestamp"],
                        "sleep_score": report["sleep_score"]
                    })
        
        return jsonify({
            "status": "success",
            "reports": reports
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True) 