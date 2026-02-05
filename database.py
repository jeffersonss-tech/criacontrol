"""
CriaControl Database - PostgreSQL Version
Adapted for cloud deployment with persistent data
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Get database URL from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_connection():
    """Get PostgreSQL connection."""
    if DATABASE_URL and DATABASE_URL.strip():
        try:
            return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        except psycopg2.OperationalError as e:
            print(f"PostgreSQL connection failed: {e}")
            print("Falling back to SQLite...")
            return get_sqlite_connection()
    else:
        print("No DATABASE_URL found, using SQLite...")
        return get_sqlite_connection()

def get_sqlite_connection():
    """Get SQLite connection (fallback for local development)."""
    import sqlite3
    user = get_current_user()
    db_file = f"data_{user['id']}.db" if user else "data.db"
    return sqlite3.connect(db_file)

# ============== USER FUNCTIONS ==============

def create_user(username, password, role='user'):
    """Create a new user."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (username, password, role)
            VALUES (%s, %s, %s)
            RETURNING id, username, role
        """, (username, password, role))
        user = cur.fetchone()
        conn.commit()
        return True, f"Usuário {username} criado com sucesso!"
    except psycopg2.IntegrityError:
        return False, "Usuário já existe!"
    except Exception as e:
        print(f"Error: {e}")
        return create_user_sqlite(username, password, role)
    finally:
        conn.close()

def authenticate(username, password):
    """Authenticate user from PostgreSQL."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, username, role 
            FROM users 
            WHERE username = %s AND password = %s
        """, (username, password))
        user = cur.fetchone()
        if user:
            return True, dict(user)
        return False, None
    except Exception as e:
        print(f"Error: {e}")
        return authenticate_sqlite(username, password)
    finally:
        conn.close()

def get_all_users():
    """Get all users (admin only) from PostgreSQL."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, username, role FROM users ORDER BY id")
        return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        print(f"Error: {e}")
        return get_all_users_sqlite()
    finally:
        conn.close()

def update_user_role(user_id, new_role):
    """Update user role in PostgreSQL."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def delete_user(user_id):
    """Delete user from PostgreSQL."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def update_user_password(user_id, new_password):
    """Update user password in PostgreSQL."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

# ============== WEIGHING FUNCTIONS ==============

def salvar_pesagem(user_id, numero_bezerro, peso_kg, sexo, raca, lote):
    """Save weighing record to PostgreSQL."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pesagens (user_id, numero_bezerro, peso_kg, sexo, raca, lote)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, numero_bezerro, peso_kg, sexo, raca, lote))
        pesagem_id = cur.fetchone()['id']
        conn.commit()
        return pesagem_id
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def obter_pesagens(user_id):
    """Get all weighings for a user from PostgreSQL."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, numero_bezerro, peso_kg, sexo, raca, lote, data_pesagem
            FROM pesagens 
            WHERE user_id = %s
            ORDER BY data_pesagem DESC, id DESC
        """, (user_id,))
        return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()

def obter_lotes(user_id):
    """Get all lots for a user from PostgreSQL."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT lote FROM pesagens WHERE user_id = %s ORDER BY lote", (user_id,))
        return [row['lote'] for row in cur.fetchall()]
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()

def obter_estatisticas(user_id):
    """Get statistics for a user from PostgreSQL."""
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
            WHERE user_id = %s
        """, (user_id,))
        stats = cur.fetchone()
        return dict(stats) if stats else None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def deletar_pesagem(user_id, pesagem_id):
    """Delete a weighing record from PostgreSQL."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM pesagens WHERE user_id = %s AND id = %s", (user_id, pesagem_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def limpar_dados(user_id):
    """Clear all data for a user from PostgreSQL."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM pesagens WHERE user_id = %s", (user_id,))
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
    with open('.session.json', 'w') as f:
        json.dump(user, f)

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

# ============== SQLITE FALLBACK FUNCTIONS ==============

def create_user_sqlite(username, password, role='user'):
    """Create user in SQLite (fallback)."""
    import sqlite3
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT DEFAULT 'user'
            )
        """)
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   (username, password, role))
        conn.commit()
        return True, f"Usuário {username} criado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Usuário já existe!"
    finally:
        conn.close()

def authenticate_sqlite(username, password):
    """Authenticate user from SQLite (fallback)."""
    import sqlite3
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?",
               (username, password))
    user = cur.fetchone()
    conn.close()
    if user:
        return True, {'id': user[0], 'username': user[1], 'role': user[2]}
    return False, None

def get_all_users_sqlite():
    """Get all users from SQLite (fallback)."""
    import sqlite3
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT id, username, role FROM users ORDER BY id")
    users = [{'id': row[0], 'username': row[1], 'role': row[2]} for row in cur.fetchall()]
    conn.close()
    return users

# ============== DATABASE SETUP ==============

def setup_database():
    """Create tables in PostgreSQL."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password VARCHAR(120) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create pesagens table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pesagens (
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
        
        # Create indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pesagens_user_id ON pesagens(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pesagens_lote ON pesagens(lote)")
        
        conn.commit()
        print("Database setup completed successfully!")
        return True
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False
    finally:
        conn.close()
