import sqlite3
import bcrypt

DB_PATH = "../data/rbac.db"

def create_user(username, password, role_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Get role_id
    cursor.execute("SELECT id FROM roles WHERE name = ?", (role_name,))
    role_id = cursor.fetchone()
    if not role_id:
        return "Invalid role."

    # Insert user
    try:
        cursor.execute("INSERT INTO users (username, password_hash, role_id) VALUES (?, ?, ?)", 
                       (username, hashed_password, role_id[0]))
        conn.commit()
    except sqlite3.IntegrityError:
        return "Username already exists."

    conn.close()
    return "User created successfully."


def authenticate_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, password_hash, role_id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    conn.close()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user[1]):
        return {"user_id": user[0], "role_id": user[2]} 
    return None
