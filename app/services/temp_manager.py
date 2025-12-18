import sqlite3, time, os
from app.core.config import TEMP_EXPIRY_SECONDS

DB = "temp.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS temp_downloads (
            task_id TEXT PRIMARY KEY,
            file_path TEXT,
            expires_at INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_temp(task_id, file_path):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO temp_downloads VALUES (?, ?, ?)
    """, (task_id, file_path, int(time.time()) + TEMP_EXPIRY_SECONDS))
    conn.commit()
    conn.close()

def get_temp(task_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT file_path, expires_at FROM temp_downloads WHERE task_id=?", (task_id,))
    row = cur.fetchone()
    conn.close()
    return row