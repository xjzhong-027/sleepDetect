from flask import Flask, request, jsonify
from flask_cors import CORS
from.models import db
from.auth import auth_bp, login_manager
from.image_processing import process_sleep_image

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # 用于会话管理

CORS(app)  # 启用 CORS 支持

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

app.register_blueprint(auth_bp)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/process_image', methods=['POST'])
@login_manager.login_required
def process():
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # 保存临时图片
    image_path = 'temp.jpg'
    file.save(image_path)

    sleep_position, output_image_path = process_sleep_image(image_path)
    os.remove(image_path)  # 删除临时图片

    if sleep_position is None:
        return jsonify({"error": "Failed to process image"}), 500

    return jsonify({"sleep_position": sleep_position, "image_path": output_image_path})

if __name__ == '__main__':
    app.run(debug=True)