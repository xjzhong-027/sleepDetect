import os

class Config:
    # MySQL配置
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3306
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '123456'  # 请替换为您的MySQL密码
    MYSQL_DB = 'sleep_app'
    
    # SQLAlchemy配置
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    SECRET_KEY = '123456'  # 请更改为一个安全的密钥
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/avatars')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit 