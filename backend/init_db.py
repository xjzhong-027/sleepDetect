import pymysql
from config import Config

def init_database():
    # 连接到MySQL服务器
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        charset='utf8mb4'
    )
    
    try:
        with conn.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"数据库 {Config.MYSQL_DB} 创建成功！")
            
    except Exception as e:
        print(f"创建数据库时出错: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_database() 