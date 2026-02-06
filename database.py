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
    conn = sqlite3.connect('criacontrol.db')
    conn.row_factory = sqlite3.Row  # IMPORTANT: Use named rows
    return conn

def get_pg_connection():
    """Get PostgreSQL connection only."""
    if DATABASE_URL.strip():
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return None

# ============== SETUP ==============

def setup_database():
    """Create tables in PostgreSQL."""
    conn = get_pg_connection()
    if not conn:
        print("No PostgreSQL URL configured")
        return False
    
    try:
        cur = conn.cursor()
        
        # Drop existing tables
        cur.execute("DROP TABLE IF EXISTS pesagens CASCADE")
        cur.execute("DROP TABLE IF EXISTS users CASCADE")
        
        # Create users table
        cur.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password VARCHAR(120) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create pesagens table
        cur.execute("""
            CREATE TABLE pesagens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                numero_bezerro VARCHAR(50) NOT NULL,
                peso_kg DECIMAL(10,2) NOT NULL,
                sexo VARCHAR(20) NOT NULL,
                raca VARCHAR(50) NOT NULL,
                lote VARCHAR(50) NOT NULL,
                data_pesagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create admin user
        cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                   ('admin', 'admin123', 'admin'))
        
        conn.commit()
        print("PostgreSQL tables created!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            conn.close()

# ============== USER FUNCTIONS ==============

def create_user(username, password, role='user'):
    """Create a new user."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   (username, password, role))
        conn.commit()
        return True, f"Usuário {username} criado!"
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
        row = cur.fetchone()
        if row:
            return True, {'id': row[0], 'username': row[1], 'role': row[2]}
        return False, None
    except Exception as e:
        print(f"Error: {e}")
        return False, None
    finally:
        conn.close()

def get_all_users():
    """Get all users."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, username, role FROM users ORDER BY id")
        return [{'id': r[0], 'username': r[1], 'role': r[2]} for r in cur.fetchall()]
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
        
        # Ensure peso_kg is a number
        peso_kg = float(peso_kg)
        
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
        print(f"Error adding pesagem: {e}")
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
            try:
                peso = float(row[2])
            except (ValueError, TypeError):
                peso = 0
            
            results.append({
                'id': row[0],
                'numero_bezerro': row[1],
                'peso_kg': peso,
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
        return [r[0] for r in cur.fetchall()]
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
            SELECT COUNT(*), SUM(peso_kg), AVG(peso_kg), MIN(peso_kg), MAX(peso_kg)
            FROM pesagens WHERE user_id = ?
        """, (user_id,))
        
        row = cur.fetchone()
        return {
            'total': row[0] or 0,
            'peso_total': float(row[1]) if row[1] else 0,
            'media_peso': float(row[2]) if row[2] else 0,
            'peso_min': float(row[3]) if row[3] else 0,
            'peso_max': float(row[4]) if row[4] else 0
        }
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
    try:
        with open('.session.json', 'w') as f:
            json.dump(user, f)
    except:
        pass

def load_session():
    try:
        with open('.session.json', 'r') as f:
            return json.load(f)
    except:
        return None

def clear_session():
    try:
        os.remove('.session.json')
    except:
        pass

def get_current_user():
    return load_session()
