"""
Sistema de Autenticação SIMPLES e ROBUSTO
"""
import sqlite3
import hashlib
import secrets
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TEXT
        )
    ''')
    
    # Criar admin padrão
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        salt = secrets.token_hex(8)
        hash_val = hashlib.sha256(('admin123' + salt).encode()).hexdigest()
        cursor.execute('INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)',
                      ('admin', f'{salt}:{hash_val}', 'admin', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def hash_password(password):
    salt = secrets.token_hex(8)
    return f'{salt}:{hashlib.sha256((password + salt).encode()).hexdigest()}'

def verify_password(password, stored):
    try:
        salt, hash_val = stored.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == hash_val
    except:
        return False

def create_user(username, password, role='user'):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return False, 'Usuário já existe'
        
        cursor.execute('INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)',
                      (username, hash_password(password), role, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True, f'Usuário {username} criado!'
    except Exception as e:
        conn.close()
        return False, str(e)

def authenticate(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(password, user[2]):
        return True, {'id': user[0], 'username': user[1], 'role': user[3]}
    return False, {}

def get_all_users():
    """Retorna todos os usuários."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role, created_at FROM users ORDER BY id')
    users = cursor.fetchall()
    conn.close()
    return [{'id': u[0], 'username': u[1], 'role': u[2], 'created_at': u[3]} for u in users]

def delete_user(user_id):
    """Deleta um usuário."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

def update_user_role(user_id, new_role):
    """Atualiza o role de um usuário."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
    conn.commit()
    conn.close()
    return True

def update_user_password(user_id, new_password):
    """Atualiza a senha de um usuário."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (hash_password(new_password), user_id))
    conn.commit()
    conn.close()
    return True

init_db()
