# ConectAção - Sistema de Voluntariado

Sistema simples e seguro para conectar voluntários com demandas de organizações.

## 🚀 Características

- ✅ **Simples**: Código limpo e direto
- ✅ **Seguro**: Hash de senhas com Werkzeug, validação de entrada
- ✅ **Funcional**: Sistema completo de cadastro, login e matching
- ✅ **Interface Amigável**: GUI com Tkinter

## 📋 Pré-requisitos

- Python 3.7+
- Tkinter (geralmente já incluído)

## 🔧 Instalação

1. **Clone o repositório**:
```bash
git clone <url>
cd Projeto-ConectAcao
```

2. **Crie e ative ambiente virtual** (recomendado):
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instale dependências**:
```bash
pip install -r requirements.txt
```

4. **Configure o arquivo .env**:
```bash
# Edite o arquivo .env com suas credenciais de admin
ADMIN_EMAIL=seu_email@exemplo.com
ADMIN_SENHA=sua_senha_segura
ADMIN_NOME=Seu Nome
```

## ▶️ Como Executar

```bash
python app.py
```

## 📖 Uso

### Login como Administrador
- Use as credenciais configuradas no arquivo `.env`
- Apenas administradores podem criar demandas

### Cadastro de Voluntários
- Na aba "Login", preencha os dados de cadastro
- Após cadastrar, faça login com suas credenciais

### Criar Demandas
- Faça login como administrador
- Vá para a aba "Demandas"
- Clique em "Criar Demanda"

### Matching
- Vá para a aba "Matching"
- Selecione uma demanda
- Clique em "Gerar Matches" para ver os voluntários mais adequados

## 📁 Estrutura do Projeto

```
Projeto-ConectAcao/
├── app.py              # Arquivo principal
├── database.py         # Módulo de banco de dados
├── auth.py             # Autenticação e segurança
├── gui.py              # Interface gráfica
├── matching.py         # Sistema de matching
├── requirements.txt    # Dependências
├── .env                # Variáveis de ambiente (não commitado)
├── .gitignore          # Arquivos ignorados pelo git
└── README.md           # Este arquivo
```

## 🔐 Segurança

- Senhas são armazenadas com hash seguro (Werkzeug)
- Validação de entrada para prevenir SQL Injection
- Credenciais de admin apenas no arquivo `.env` (não commitado)
- Uso de context managers para conexões seguras com banco

## 🛠️ Tecnologias

- **Python 3.7+**
- **SQLite**: Banco de dados
- **Tkinter**: Interface gráfica
- **Werkzeug**: Hash de senhas
- **python-dotenv**: Variáveis de ambiente

## 📝 Licença

Este projeto é de código aberto para fins educacionais.

---

**Desenvolvido com ❤️ para conectar pessoas e causas**

