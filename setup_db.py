"""
Script para inicializar o banco de dados
Roda: python setup_db.py
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get('DATABASE_URL')

def setup_postgres():
    """Cria tabelas no PostgreSQL."""
    if not DATABASE_URL:
        print("DATABASE_URL não encontrada!")
        return False
    
    print("Conectando ao PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Drop tables if exist (para limpar dados antigos)
    cur.execute("DROP TABLE IF EXISTS pesagens CASCADE")
    cur.execute("DROP TABLE IF EXISTS users CASCADE")
    
    print("Criando tabelas...")
    
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
    
    # Create indexes
    cur.execute("CREATE INDEX idx_pesagens_user_id ON pesagens(user_id)")
    cur.execute("CREATE INDEX idx_pesagens_lote ON pesagens(lote)")
    
    # Create default admin user
    cur.execute("""
        INSERT INTO users (username, password, role)
        VALUES ('admin', 'admin123', 'admin')
    """)
    
    conn.commit()
    print("Tabelas criadas com sucesso!")
    print("Admin user: admin / admin123")
    
    conn.close()
    return True

if __name__ == "__main__":
    if setup_postgres():
        print("\n✅ Banco de dados configurado!")
    else:
        print("\n❌ Erro ao configurar banco!")
