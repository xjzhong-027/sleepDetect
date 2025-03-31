from flask import Flask, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from config import Config
from functools import wraps
from flask_cors import CORS
app = Flask(__name__)
app.config.from_object(Config)
# 初始化CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 初始化数据库
db = SQLAlchemy(app)
jwt = JWTManager(app)

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sleep_records = db.relationship('SleepRecord', backref='user', lazy=True)

# 睡眠记录模型
class SleepRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    sleep_time = db.Column(db.DateTime, nullable=False)
    wake_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer)  # 睡眠时长（分钟）
    score = db.Column(db.Integer)  # 睡眠评分
    emotion_data = db.Column(db.JSON)  # 情绪数据
    wake_count = db.Column(db.Integer)  # 夜起次数
    posture_data = db.Column(db.JSON)  # 姿势数据
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# JWT token验证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# 用户注册
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password_hash=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'message': '注册成功',
        'user': {
            'id': new_user.id,
            'username': new_user.username
        }
    }), 201

# 用户登录
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }, app.config['SECRET_KEY'])
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'avatar': user.avatar
            }
        })
    
    return jsonify({'message': '用户名或密码错误'}), 401

# 检查认证状态
@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'isLoggedIn': False})
    
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        user = User.query.get(data['user_id'])
        if user:
            return jsonify({
                'isLoggedIn': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'avatar': user.avatar
                }
            })
    except:
        pass
    
    return jsonify({'isLoggedIn': False})

# 上传头像
@app.route('/api/upload-avatar', methods=['POST'])
@token_required
def upload_avatar(current_user):
    if 'avatar' not in request.files:
        return jsonify({'message': '没有文件'}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'message': '没有选择文件'}), 400
    
    if file:
        filename = f"avatar_{current_user.id}_{int(datetime.utcnow().timestamp())}.jpg"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        current_user.avatar = f'/static/avatars/{filename}'
        db.session.commit()
        
        return jsonify({
            'message': '头像上传成功',
            'avatarUrl': current_user.avatar
        })

# 获取用户统计数据
@app.route('/api/user-stats', methods=['GET'])
@token_required
def get_user_stats(current_user):
    records = SleepRecord.query.filter_by(user_id=current_user.id).all()
    
    total_days = len(records)
    if total_days == 0:
        return jsonify({
            'totalSleepDays': 0,
            'averageScore': 0,
            'bestScore': 0
        })
    
    total_score = sum(record.score for record in records)
    best_score = max(record.score for record in records)
    
    return jsonify({
        'totalSleepDays': total_days,
        'averageScore': round(total_score / total_days),
        'bestScore': best_score
    })

# 保存睡眠记录
@app.route('/api/sleep-record', methods=['POST'])
@token_required
def save_sleep_record(current_user):
    data = request.get_json()
    
    new_record = SleepRecord(
        user_id=current_user.id,
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        sleep_time=datetime.fromisoformat(data['sleep_time']),
        wake_time=datetime.fromisoformat(data['wake_time']),
        duration=data['duration'],
        score=data['score'],
        emotion_data=data['emotion_data'],
        wake_count=data['wake_count'],
        posture_data=data['posture_data']
    )
    
    db.session.add(new_record)
    db.session.commit()
    
    return jsonify({'message': '记录保存成功'}), 201

# 获取睡眠记录
@app.route('/api/sleep-records', methods=['GET'])
@token_required
def get_sleep_records(current_user):
    records = SleepRecord.query.filter_by(user_id=current_user.id).order_by(SleepRecord.date.desc()).all()
    
    return jsonify([{
        'id': record.id,
        'date': record.date.strftime('%Y-%m-%d'),
        'sleep_time': record.sleep_time.isoformat(),
        'wake_time': record.wake_time.isoformat(),
        'duration': record.duration,
        'score': record.score,
        'emotion_data': record.emotion_data,
        'wake_count': record.wake_count,
        'posture_data': record.posture_data
    } for record in records])

# 退出登录
@app.route('/api/logout', methods=['POST'])
@token_required
def logout(current_user):
    # 由于使用JWT，客户端只需要删除token即可
    return jsonify({'message': '退出成功'})

if __name__ == '__main__':
    with app.app_context():
        # 创建所有数据库表
        db.create_all()
    app.run(debug=True)