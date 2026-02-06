"""
CriaControl Database - PostgreSQL + SQLite Version
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json

DATABASE_URL = os.environ.get('DATABASE_URL', '')

def get_connection():
    """Get database connection (PostgreSQL or SQLite)."""
    if DATABASE_URL.strip():
        try:
            return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        except psycopg2.OperationalError:
            print("Falling back to SQLite...")
            return get_sqlite_connection()
    else:
        return get_sqlite_connection()

def get_sqlite_connection():
    """Get SQLite connection."""
    import sqlite3
    return sqlite3.connect('criacontrol.db')

# ============== USER FUNCTIONS ==============

def create_user(username, password, role='user'):
    """Create a new user."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # Create tables if not exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pesagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                numero_bezerro TEXT NOT NULL,
                peso_kg REAL NOT NULL,
                sexo TEXT NOT NULL,
                raca TEXT NOT NULL,
                lote TEXT NOT NULL,
                data_pesagem TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   (username, password, role))
        conn.commit()
        return True, f"Usuário {username} criado com sucesso!"
    except Exception as e:
        print(f"Error: {e}")
        return False, "Usuário já existe!"
    finally:
        conn.close()

def authenticate(username, password):
    """Authenticate user."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?",
                   (username, password))
        user = cur.fetchone()
        if user:
            return True, {'id': user[0], 'username': user[1], 'role': user[2]}
        return False, None
    except Exception as e:
        print(f"Error: {e}")
        return False, None
    finally:
        conn.close()

def get_all_users():
    """Get all users (admin only)."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, username, role FROM users ORDER BY id")
        return [{'id': row[0], 'username': row[1], 'role': row[2]} for row in cur.fetchall()]
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()

def update_user_role(user_id, new_role):
    """Update user role."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def delete_user(user_id):
    """Delete user."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def update_user_password(user_id, new_password):
    """Update user password."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

# ============== WEIGHING FUNCTIONS ==============

def adicionar_pesagem(user_id, numero_bezerro, peso_kg, sexo, raca, lote, data=None, hora=None, obs=None):
    """Add weighing record."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        if data and hora:
            data_pesagem = f"{data} {hora}"
        else:
            from datetime import datetime
            data_pesagem = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cur.execute("""
            INSERT INTO pesagens (user_id, numero_bezerro, peso_kg, sexo, raca, lote, data_pesagem)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, numero_bezerro, peso_kg, sexo, raca, lote, data_pesagem))
        
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def obter_pesagens(user_id):
    """Get all weighings for a user."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, numero_bezerro, peso_kg, sexo, raca, lote, data_pesagem
            FROM pesagens 
            WHERE user_id = ?
            ORDER BY data_pesagem DESC, id DESC
        """, (user_id,))
        
        results = []
        for row in cur.fetchall():
            results.append({
                'id': row[0],
                'numero_bezerro': row[1],
                'peso_kg': row[2],
                'sexo': row[3],
                'raca': row[4],
                'lote': row[5],
                'data_pesagem': row[6]
            })
        return results
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()

def obter_lotes(user_id):
    """Get all lots for a user."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT lote FROM pesagens WHERE user_id = ? ORDER BY lote", (user_id,))
        return [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()

def obter_estatisticas(user_id):
    """Get statistics for a user."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(peso_kg) as peso_total,
                AVG(peso_kg) as media_peso,
                MIN(peso_kg) as peso_min,
                MAX(peso_kg) as peso_max
            FROM pesagens 
            WHERE user_id = ?
        """, (user_id,))
        
        row = cur.fetchone()
        if row:
            return {
                'total': row[0] or 0,
                'peso_total': row[1] or 0,
                'media_peso': row[2] or 0,
                'peso_min': row[3] or 0,
                'peso_max': row[4] or 0
            }
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def deletar_pesagem(user_id, pesagem_id):
    """Delete a weighing record."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM pesagens WHERE user_id = ? AND id = ?", (user_id, pesagem_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def limpar_dados(user_id):
    """Clear all data for a user."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM pesagens WHERE user_id = ?", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

# ============== SESSION FUNCTIONS ==============

def save_session(user):
    """Save session to file."""
    try:
        with open('.session.json', 'w') as f:
            json.dump(user, f)
    except:
        pass

def load_session():
    """Load session from file."""
    try:
        with open('.session.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def clear_session():
    """Clear session file."""
    try:
        os.remove('.session.json')
    except FileNotFoundError:
        pass

def get_current_user():
    """Get current user from session."""
    return load_session()
