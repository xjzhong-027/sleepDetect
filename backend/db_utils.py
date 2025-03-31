import mysql.connector
from mysql.connector import Error, pooling
import logging
from datetime import datetime, date
import time
import threading

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '123456',
            'database': 'posture',
            'port': 3306,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'pool_name': 'posture_pool',
            'pool_size': 5
        }
        self.connection_pool = None
        self.lock = threading.Lock()
        self._initialize_pool()
        self._create_tables()

    def _initialize_pool(self):
        """初始化连接池"""
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(**self.db_config)
            logger.info("数据库连接池初始化成功")
        except Error as e:
            logger.error(f"初始化数据库连接池失败: {e}")
            raise

    def _get_connection(self):
        """从连接池获取连接"""
        try:
            return self.connection_pool.get_connection()
        except Error as e:
            logger.error(f"获取数据库连接失败: {e}")
            raise

    def _create_tables(self):
        """创建必要的数据表"""
        create_posture_records = """
        CREATE TABLE IF NOT EXISTS posture_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            posture_type VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
            timestamp DATETIME,
            duration INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        create_posture_statistics = """
        CREATE TABLE IF NOT EXISTS posture_statistics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE,
            posture_type VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
            total_duration INT DEFAULT 0,
            count INT DEFAULT 0,
            UNIQUE KEY date_posture (date, posture_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        try:
            connection = self._get_connection()
            with connection.cursor() as cursor:
                # 先删除已存在的表
                cursor.execute("DROP TABLE IF EXISTS posture_records")
                cursor.execute("DROP TABLE IF EXISTS posture_statistics")
                
                # 创建新表
                cursor.execute(create_posture_records)
                cursor.execute(create_posture_statistics)
                connection.commit()
                logger.info("数据表创建/检查完成")
        except Error as e:
            logger.error(f"创建数据表失败: {e}")
            raise
        finally:
            if connection:
                connection.close()

    def save_posture(self, posture_type, timestamp, duration):
        """保存姿势记录"""
        with self.lock:
            try:
                connection = self._get_connection()
                with connection.cursor() as cursor:
                    # 保存姿势记录
                    insert_record = """
                    INSERT INTO posture_records (posture_type, timestamp, duration)
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(insert_record, (posture_type, timestamp, duration))

                    # 更新统计数据
                    record_date = timestamp.date()
                    update_stats = """
                    INSERT INTO posture_statistics (date, posture_type, total_duration, count)
                    VALUES (%s, %s, %s, 1)
                    ON DUPLICATE KEY UPDATE
                    total_duration = total_duration + VALUES(total_duration),
                    count = count + 1
                    """
                    cursor.execute(update_stats, (record_date, posture_type, duration))

                    connection.commit()
                    logger.info(f"保存姿势记录成功: {posture_type}, 持续时间: {duration}秒")
                    return True
            except Error as e:
                logger.error(f"保存姿势记录失败: {e}")
                if connection:
                    connection.rollback()
                return False
            finally:
                if connection:
                    connection.close()

    def get_daily_statistics(self, target_date=None):
        """获取每日统计数据"""
        target_date = target_date or date.today()
        try:
            connection = self._get_connection()
            with connection.cursor(dictionary=True) as cursor:
                query = """
                SELECT posture_type, total_duration, count
                FROM posture_statistics
                WHERE date = %s
                """
                cursor.execute(query, (target_date,))
                results = cursor.fetchall()
                return results if results else []
        except Error as e:
            logger.error(f"获取统计数据失败: {e}")
            return []
        finally:
            if connection:
                connection.close()

    def get_posture_history(self, start_time=None, end_time=None, limit=100):
        """获取历史记录"""
        try:
            connection = self._get_connection()
            with connection.cursor(dictionary=True) as cursor:
                query = """
                SELECT posture_type, timestamp, duration
                FROM posture_records
                WHERE 1=1
                """
                params = []

                if start_time:
                    query += " AND timestamp >= %s"
                    params.append(start_time)
                if end_time:
                    query += " AND timestamp <= %s"
                    params.append(end_time)

                query += " ORDER BY timestamp DESC LIMIT %s"
                params.append(limit)

                cursor.execute(query, params)
                return cursor.fetchall()
        except Error as e:
            logger.error(f"获取历史记录失败: {e}")
            return []
        finally:
            if connection:
                connection.close()

    def close(self):
        """关闭连接池"""
        if self.connection_pool:
            self.connection_pool.close() 