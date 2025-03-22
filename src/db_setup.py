import sqlite3

DB_PATH = "../data/rbac.db"

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role_id INTEGER NOT NULL,
        FOREIGN KEY (role_id) REFERENCES roles(id)
    )
    """)

    # Create Roles Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)

    # Create Permissions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_id INTEGER NOT NULL,
        document_category TEXT NOT NULL,
        FOREIGN KEY (role_id) REFERENCES roles(id)
    )
    """)

    # Create Documents Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL
    )
    """)

    # Create Access Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS access_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        doc_id INTEGER NOT NULL,
        access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        access_status TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (doc_id) REFERENCES documents(id)
    )
    """)

    # Insert Default Roles
    cursor.executemany("INSERT OR IGNORE INTO roles (name) VALUES (?)", [
        ("admin",), 
        ("researcher",), 
        ("student",)
    ])

    # Insert Default Permissions
    cursor.executemany("INSERT OR IGNORE INTO permissions (role_id, document_category) VALUES (?, ?)", [
        (1, "all"),  # Admin can access all documents
        (2, "research"),  # Researcher can access research docs
        (3, "general")  # Students have limited access
    ])

    conn.commit()
    conn.close()
    print("Database setup complete.")

if __name__ == "__main__":
    setup_database()
