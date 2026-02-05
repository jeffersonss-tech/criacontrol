# CriaControl - Sistema de Pesagem de Bezerros

## SIMPLES E ROBUSTO 🐄

### Como usar:

1. **Instalar dependências:**
   ```
   pip install streamlit pandas
   ```

2. **Rodar o app:**
   ```
   iniciar.bat
   ```

3. **Login padrão:**
   - Usuário: `admin`
   - Senha: `admin123`

### Cada usuário tem seus próprios dados!

- Cada usuário = 1 banco de dados separado
- Os dados são isolados automaticamente
- Ninguém vê os dados dos outros

### Funcionalidades:

- 📊 Dashboard com estatísticas
- ➕ Nova Pesagem
- 📋 Consultar e filtrar
- 📈 Relatórios por lote/sexo/raça
- 🗑️ Deletar e limpar dados

### Estrutura:

```
criacontrol_novo/
├── app.py           # Interface Streamlit
├── auth.py          # Sistema de login
├── database.py     # Banco de dados (1 por usuário!)
├── requirements.txt
└── iniciar.bat      # Rodar o app
```

### Criar novos usuários:

Na página de login, expanda "Criar novo usuário" e preencha os dados.
