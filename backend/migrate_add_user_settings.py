"""
数据库迁移脚本：为 users 表添加 settings 字段
运行方式: python migrate_add_user_settings.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "app", "app.db")

def migrate():
    if not os.path.exists(DB_PATH):
        print("数据库文件不存在，跳过迁移（首次启动时会自动创建）")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 检查 settings 字段是否已存在
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]

    if "settings" in columns:
        print("settings 字段已存在，无需迁移")
    else:
        cursor.execute("ALTER TABLE users ADD COLUMN settings JSON DEFAULT '{}'")
        conn.commit()
        print("迁移成功：已为 users 表添加 settings 字段")

    conn.close()

if __name__ == "__main__":
    migrate()
