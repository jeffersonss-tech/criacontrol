"""
Banco de dados SIMPLES e ROBUSTO
Cada usuário = sua própria fazenda
"""
import sqlite3
import os
import secrets
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "pesagem.db")
SESSION_PATH = os.path.join(os.path.dirname(__file__), "session.json")

def get_db_path(user_id):
    """Cada usuário tem seu próprio arquivo de banco!"""
    return os.path.join(os.path.dirname(__file__), f"data_{user_id}.db")

def init_user_db(user_id):
    """Inicializa o banco de um usuário específico."""
    db_file = get_db_path(user_id)
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pesagem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_bezerro TEXT NOT NULL,
            lote TEXT NOT NULL,
            data_pesagem TEXT NOT NULL,
            horario_pesagem TEXT NOT NULL,
            sexo TEXT NOT NULL,
            raca TEXT NOT NULL,
            peso_kg REAL NOT NULL,
            observacoes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# ===== SESSÃO PERSISTENTE =====
def save_session(user):
    """Salva sessão em arquivo para persistência."""
    token = secrets.token_hex(16)
    session = {
        'token': token,
        'user_id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'created_at': datetime.now().isoformat()
    }
    with open(SESSION_PATH, 'w', encoding='utf-8') as f:
        json.dump(session, f)
    return token

def load_session():
    """Carrega sessão persistente."""
    if os.path.exists(SESSION_PATH):
        try:
            with open(SESSION_PATH, 'r', encoding='utf-8') as f:
                session = json.load(f)
                return {
                    'id': session['user_id'],
                    'username': session['username'],
                    'role': session['role']
                }
        except:
            return None
    return None

def clear_session():
    """Limpa sessão (logout)."""
    if os.path.exists(SESSION_PATH):
        os.remove(SESSION_PATH)

def adicionar_pesagem(user_id, numero, lote, data, horario, sexo, raca, peso, obs=''):
    """Adiciona pesagem ao banco DO USUÁRIO."""
    db_file = get_db_path(user_id)
    
    # Se o arquivo não existe, cria
    if not os.path.exists(db_file):
        init_user_db(user_id)
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO pesagem (numero_bezerro, lote, data_pesagem, horario_pesagem, sexo, raca, peso_kg, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (numero, lote, data, horario, sexo, raca, peso, obs))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def obter_pesagens(user_id):
    """Obtém TODAS as pesagens DO USUÁRIO."""
    db_file = get_db_path(user_id)
    
    if not os.path.exists(db_file):
        return []
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pesagem ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(zip(['id', 'numero_bezerro', 'lote', 'data_pesagem', 'horario_pesagem', 'sexo', 'raca', 'peso_kg', 'observacoes', 'created_at'], row)) for row in rows]

def obter_estatisticas(user_id):
    """Obtém estatísticas DO USUÁRIO."""
    pesagens = obter_pesagens(user_id)
    
    if not pesagens:
        return {'total': 0, 'peso_total': 0, 'peso_medio': 0}
    
    pesos = [p['peso_kg'] for p in pesagens]
    
    return {
        'total': len(pesos),
        'peso_total': sum(pesos),
        'peso_medio': sum(pesos) / len(pesos)
    }

def obter_lotes(user_id):
    """Obtém lotes DO USUÁRIO."""
    pesagens = obter_pesagens(user_id)
    return sorted(list(set([p['lote'] for p in pesagens])))

def deletar_pesagem(user_id, pesagem_id):
    """Deleta uma pesagem DO USUÁRIO."""
    db_file = get_db_path(user_id)
    
    if not os.path.exists(db_file):
        return False
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM pesagem WHERE id = ?', (pesagem_id,))
    conn.commit()
    conn.close()
    return True

def limpar_dados(user_id):
    """Limpa TODOS os dados DO USUÁRIO."""
    db_file = get_db_path(user_id)
    
    if os.path.exists(db_file):
        os.remove(db_file)
    
    init_user_db(user_id)
    return True

def gerar_id_automatico():
    """Gera ID automático no formato: BZ-YYYYMMDD-XXXX"""
    import uuid
    from datetime import datetime
    data = datetime.now().strftime("%Y%m%d")
    uid = str(uuid.uuid4())[:4].upper()
    return f"BZ-{data}-{uid}"
