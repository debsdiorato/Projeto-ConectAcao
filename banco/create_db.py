# create_db.py
import sqlite3
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()
DB = os.getenv("DB_FILENAME", "voluntarios.db")

schema = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    papel TEXT NOT NULL DEFAULT 'voluntario'
);

CREATE TABLE IF NOT EXISTS voluntarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    habilidades TEXT,
    disponibilidade TEXT,
    cidade TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS demandas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    habilidades_requeridas TEXT NOT NULL
);
"""


def create_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.executescript(schema)
    conn.commit()

    # cria admin padrão a partir do .env ou valores default
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_pass_plain = os.getenv("ADMIN_PASS", "admin123")

    c.execute("SELECT id FROM usuarios WHERE email = ?", (admin_email,))
    if not c.fetchone():
        c.execute("INSERT INTO usuarios (nome, telefone, email, senha_hash, papel) VALUES (?, ?, ?, ?, ?)",
                  ("Admin", "000000000", admin_email, generate_password_hash(admin_pass_plain), "admin"))

    # cria usuário voluntário de exemplo
    volunteer_email = "joao@example.com"
    c.execute("SELECT id FROM usuarios WHERE email = ?", (volunteer_email,))
    if not c.fetchone():
        hash_ = generate_password_hash("vol123")
        c.execute("INSERT INTO usuarios (nome, telefone, email, senha_hash, papel) VALUES (?, ?, ?, ?, ?)",
                  ("João", "11999999999", volunteer_email, hash_, "voluntario"))
        user_id = c.lastrowid
        c.execute("INSERT INTO voluntarios (usuario_id, habilidades, disponibilidade, cidade) VALUES (?, ?, ?, ?)",
                  (user_id, "força, transporte", "manhã", "Rio Bonito do Iguaçu"))

    # cria demanda exemplo
    c.execute("SELECT id FROM demandas WHERE titulo = ?", ("Remover entulhos",))
    if not c.fetchone():
        c.execute("INSERT INTO demandas (titulo, habilidades_requeridas) VALUES (?, ?)",
                  ("Remover entulhos", "força, transporte"))

    conn.commit()
    conn.close()
    print(f"Banco criado/populado em {DB}")

if __name__ == "__main__":
    create_db()
