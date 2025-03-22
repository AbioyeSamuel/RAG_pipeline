import sqlite3

DB_PATH = "../data/rbac.db"

def get_user_permissions(role_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT document_category FROM permissions WHERE role_id = ?", (role_id,))
    permissions = cursor.fetchall()

    conn.close()
    return [perm[0] for perm in permissions]

def filter_documents_by_role(role_id, documents):
    allowed_categories = get_user_permissions(role_id)
    
    if "all" in allowed_categories:
        return documents  # Admin gets full access

    return [doc for doc in documents if doc.metadata.get("category") in allowed_categories]
