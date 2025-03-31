from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 启用 CORS
# 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+mysqlconnector://root:123456@localhost/users'
# 请将 'root' 替换为你的 MySQL 用户名，'password' 替换为你的密码，'users' 替换为你的数据库名
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定义用户模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

# 注册接口
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({"message": "用户名、密码和邮箱不能为空"}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "该用户名已被注册"}), 400

    new_user = User(username=username, password=password, email=email)
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "注册成功"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"注册失败: {str(e)}"}), 500

# 登录接口
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username, password=password).first()
    if user:
        return jsonify({"message": "登录成功"}), 200
    else:
        return jsonify({"message": "用户名或密码错误"}), 401

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)