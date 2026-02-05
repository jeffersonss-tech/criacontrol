# CriaControl - Sistema de Pesagem de Bezerros

## 🐄 Sistema Completo com PostgreSQL

---

## 🚀 Deploy no Streamlit Cloud

### 1. Criar PostgreSQL Grátis (Supabase)

1. Acesse: **https://supabase.com**
2. Clique em "Start your project" → "New Project"
3. Preencha:
   - **Name:** `criacontrol`
   - **Database Password:** Anote a senha!
4. Aguarde criar (2-3 minutos)
5. Vá em **Settings** → **Database** → **Connection string**
6. Copie a URL (formato: `postgresql://user:pass@host:5432/db`)

### 2. Configurar no Streamlit Cloud

1. Acesse: **https://share.streamlit.io**
2. Selecione o repositório `jeffersonss-tech/criacontrol`
3. Em **Advanced settings** → **Secrets**, adicione:
   ```toml
   DATABASE_URL = "postgresql://seu-usuario:sua-senha@host:5432/db"
   ```

### 3. Deploy

1. Clique em **Deploy!**
2. Aguarde build e start (~2-3 minutos)
3. Acesse a URL gerada!

---

## 💻 Desenvolvimento Local

### Sem PostgreSQL (SQLite):
```bash
pip install streamlit pandas fpdf openpyxl matplotlib
streamlit run app.py
```

### Com PostgreSQL local:
```bash
pip install streamlit pandas fpdf openpyxl matplotlib psycopg2-binary
export DATABASE_URL="postgresql://user:pass@localhost:5432/db"
streamlit run app.py
```

### Setup do banco:
```bash
python -c "import database; database.setup_database()"
```

---

## 🔐 Login Padrão

- **Usuário:** `admin`
- **Senha:** `admin123`

---

## 📊 Funcionalidades

- 📊 Dashboard com estatísticas e gráficos
- ➕ Nova Pesagem (ID automático)
- 📋 Consultar e filtrar por lote
- 📈 Relatórios (Excel + PDF)
- 👥 Gerenciar usuários (admin)
- 🔐 Dados persistentes no PostgreSQL

---

## 🎯 Cada Usuário = Dados Isolados

- Os dados são filtrados por `user_id`
- Cada usuário só vê suas próprias pesagens
- Administrador pode gerenciar todos os usuários

---

## 📁 Estrutura

```
criacontrol/
├── app.py           # Interface Streamlit
├── auth.py          # Sistema de autenticação
├── database.py      # Banco PostgreSQL + SQLite fallback
├── requirements.txt # Dependências
├── iniciar.bat      # Script de inicialização (Windows)
└── README.md        # Este arquivo
```

---

## 🛠️ Technologies

- **Streamlit** - Interface web
- **PostgreSQL** - Banco de dados cloud
- **Python** - Lógica
- **Pandas** - Manipulação de dados
- **FPDF** - Geração de PDFs
- **Openpyxl** - Exportação Excel

---

## 📝 Licença

MIT License - Feito com ❤️ para o agronegócio brasileiro 🇧🇷
