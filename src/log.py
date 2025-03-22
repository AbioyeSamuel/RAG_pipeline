import sqlite3
from datetime import datetime

DB_PATH = "../data/rbac.db"

def log_access(user_id, doc_id, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO access_logs (user_id, doc_id, access_status, access_time)
        VALUES (?, ?, ?, ?)
    """, (user_id, doc_id, status, datetime.now()))
    
    conn.commit()
    conn.close()
