from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import requests
import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('api_gateway.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 服务配置
SERVICES = {
    'emotion': {
        'url': 'http://127.0.0.1:5000',
        'routes': ['/video_feed', '/api/getData', '/health', '/start_monitoring', '/stop_monitoring', '/get_monitoring_data', '/toggle_feature']
    },
    'posture': {
        'url': 'http://127.0.0.1:5001',
        'routes': [
            '/video_feed', 
            '/api/getData', 
            '/health', 
            '/start_monitoring', 
            '/stop_monitoring', 
            '/get_monitoring_data', 
            '/toggle_feature', 
            '/check_camera',
            '/get_statistics',
            '/get_history'
        ]
    }
}

def forward_request(service_name, path, method='GET', data=None):
    """转发请求到对应的服务"""
    if service_name not in SERVICES:
        return jsonify({'error': 'Service not found'}), 404

    service = SERVICES[service_name]
    
    # 移除路径前缀（如 /posture/ 或 /emotion/）
    clean_path = path
    if path.startswith(f'/{service_name}/'):
        clean_path = path[len(f'/{service_name}/'):]
    
    if clean_path not in service['routes']:
        return jsonify({'error': 'Route not found'}), 404

    try:
        url = f"{service['url']}/{clean_path}"
        
        # 设置通用请求头
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # 根据请求类型发送请求
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        
        # 创建响应对象
        response_obj = Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'application/json')
        )
        
        # 复制所有响应头
        for key, value in response.headers.items():
            if key.lower() not in ['content-length', 'content-encoding']:
                response_obj.headers[key] = value
                
        return response_obj
    except requests.exceptions.RequestException as e:
        logger.error(f"Error forwarding request to {service_name}: {e}")
        return jsonify({'error': 'Service unavailable'}), 503

@app.route('/emotion/<path:path>', methods=['GET', 'POST'])
def emotion_service(path):
    """处理情绪检测服务的请求"""
    return forward_request('emotion', f'/{path}', request.method, request.get_json())

@app.route('/posture/<path:path>', methods=['GET', 'POST'])
def posture_service(path):
    """处理姿势检测服务的请求"""
    return forward_request('posture', f'/{path}', request.method, request.get_json())

@app.route('/health')
def health_check():
    """检查所有服务的健康状态"""
    health_status = {}
    for service_name, service in SERVICES.items():
        try:
            response = requests.get(f"{service['url']}/health")
            health_status[service_name] = response.json()
        except:
            health_status[service_name] = {'status': 'unavailable'}
    
    return jsonify(health_status)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=False, threaded=True) 