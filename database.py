"""Módulo de banco de dados - SQLite com segurança."""
import sqlite3
from contextlib import contextmanager

DB_FILE = "voluntarios.db"


def migrar_banco():
    """Migra banco de dados antigo para nova estrutura."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Verificar se a tabela demandas existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='demandas'")
        if cursor.fetchone():
            # Verificar estrutura da tabela
            cursor.execute("PRAGMA table_info(demandas)")
            colunas = [row[1] for row in cursor.fetchall()]
            
            if 'habilidades_requeridas' in colunas:
                # Backup dos dados existentes (se houver)
                try:
                    cursor.execute("SELECT id, titulo FROM demandas")
                    dados_antigos = cursor.fetchall()
                except:
                    dados_antigos = []
                
                # Remover tabelas antigas
                cursor.execute("DROP TABLE IF EXISTS demanda_habilidades")
                cursor.execute("DROP TABLE IF EXISTS demandas")
                
                # Recriar tabela com estrutura nova
                cursor.execute("""
                    CREATE TABLE demandas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        titulo TEXT NOT NULL,
                        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Restaurar dados (sem habilidades_requeridas)
                for row in dados_antigos:
                    cursor.execute(
                        "INSERT INTO demandas (id, titulo) VALUES (?, ?)",
                        (row[0], row[1])
                    )
                
                conn.commit()
    except Exception as e:
        # Se der erro, tenta continuar
        conn.rollback()
    finally:
        conn.close()


def init_db():
    """Inicializa o banco de dados criando as tabelas necessárias."""
    # Executar migração primeiro
    migrar_banco()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Tabela de habilidades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habilidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL
            )
        """)
        
        # Tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                papel TEXT DEFAULT 'voluntario' CHECK(papel IN ('voluntario', 'admin'))
            )
        """)
        
        # Tabela de voluntários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voluntarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                disponibilidade TEXT,
                cidade TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de relação voluntário-habilidades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voluntario_habilidades (
                voluntario_id INTEGER NOT NULL,
                habilidade_id INTEGER NOT NULL,
                PRIMARY KEY (voluntario_id, habilidade_id),
                FOREIGN KEY (voluntario_id) REFERENCES voluntarios(id) ON DELETE CASCADE,
                FOREIGN KEY (habilidade_id) REFERENCES habilidades(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de demandas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demandas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de relação demanda-habilidades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demanda_habilidades (
                demanda_id INTEGER NOT NULL,
                habilidade_id INTEGER NOT NULL,
                PRIMARY KEY (demanda_id, habilidade_id),
                FOREIGN KEY (demanda_id) REFERENCES demandas(id) ON DELETE CASCADE,
                FOREIGN KEY (habilidade_id) REFERENCES habilidades(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        
        # Popular habilidades padrão
        popular_habilidades_padrao()


@contextmanager
def get_connection():
    """Context manager para conexões seguras com o banco."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def criar_usuario(nome, email, senha_hash, papel='voluntario'):
    """Cria um novo usuário."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, papel) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, papel)
        )
        return cursor.lastrowid


def buscar_usuario_por_email(email):
    """Busca usuário por email."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None


def popular_habilidades_padrao():
    """Popula o banco com habilidades padrão."""
    habilidades_padrao = [
        "Engenharia", "Marketing", "Pedreiro", "Enfermagem", "Educação",
        "Design", "Programação", "Contabilidade", "Advocacia", "Medicina",
        "Psicologia", "Arquitetura", "Jornalismo", "Fotografia", "Culinária",
        "Música", "Artes", "Esportes", "Idiomas", "Administração"
    ]
    
    with get_connection() as conn:
        cursor = conn.cursor()
        for hab in habilidades_padrao:
            try:
                cursor.execute("INSERT OR IGNORE INTO habilidades (nome) VALUES (?)", (hab,))
            except:
                pass
        conn.commit()


def listar_habilidades():
    """Lista todas as habilidades disponíveis."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM habilidades ORDER BY nome")
        return [dict(row) for row in cursor.fetchall()]


def criar_voluntario(usuario_id, habilidades_ids, disponibilidade="", cidade=""):
    """Cria perfil de voluntário com habilidades."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO voluntarios (usuario_id, disponibilidade, cidade) VALUES (?, ?, ?)",
            (usuario_id, disponibilidade, cidade)
        )
        voluntario_id = cursor.lastrowid
        
        # Adicionar habilidades
        for hab_id in habilidades_ids:
            cursor.execute(
                "INSERT INTO voluntario_habilidades (voluntario_id, habilidade_id) VALUES (?, ?)",
                (voluntario_id, hab_id)
            )


def listar_voluntarios():
    """Lista todos os voluntários com suas habilidades."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.id, v.usuario_id, v.disponibilidade, v.cidade, u.nome, u.email
            FROM voluntarios v
            JOIN usuarios u ON u.id = v.usuario_id
        """)
        voluntarios = [dict(row) for row in cursor.fetchall()]
        
        # Adicionar habilidades para cada voluntário
        for vol in voluntarios:
            cursor.execute("""
                SELECT h.id, h.nome
                FROM habilidades h
                JOIN voluntario_habilidades vh ON h.id = vh.habilidade_id
                WHERE vh.voluntario_id = ?
            """, (vol['id'],))
            vol['habilidades'] = [dict(row) for row in cursor.fetchall()]
            vol['habilidades_nomes'] = [h['nome'] for h in vol['habilidades']]
        
        return voluntarios


def criar_demanda(titulo, habilidades_ids):
    """Cria uma nova demanda com habilidades."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO demandas (titulo) VALUES (?)", (titulo,))
        demanda_id = cursor.lastrowid
        
        # Adicionar habilidades
        for hab_id in habilidades_ids:
            cursor.execute(
                "INSERT INTO demanda_habilidades (demanda_id, habilidade_id) VALUES (?, ?)",
                (demanda_id, hab_id)
            )
        return demanda_id


def listar_demandas():
    """Lista todas as demandas com suas habilidades."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM demandas ORDER BY criado_em DESC")
        demandas = [dict(row) for row in cursor.fetchall()]
        
        # Adicionar habilidades para cada demanda
        for dem in demandas:
            cursor.execute("""
                SELECT h.id, h.nome
                FROM habilidades h
                JOIN demanda_habilidades dh ON h.id = dh.habilidade_id
                WHERE dh.demanda_id = ?
            """, (dem['id'],))
            dem['habilidades'] = [dict(row) for row in cursor.fetchall()]
            dem['habilidades_nomes'] = [h['nome'] for h in dem['habilidades']]
            dem['habilidades_requeridas'] = ", ".join(dem['habilidades_nomes'])
        
        return demandas


def buscar_demanda_por_id(demanda_id):
    """Busca demanda por ID com habilidades."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM demandas WHERE id = ?", (demanda_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        demanda = dict(row)
        
        # Buscar habilidades
        cursor.execute("""
            SELECT h.id, h.nome
            FROM habilidades h
            JOIN demanda_habilidades dh ON h.id = dh.habilidade_id
            WHERE dh.demanda_id = ?
        """, (demanda_id,))
        demanda['habilidades'] = [dict(row) for row in cursor.fetchall()]
        demanda['habilidades_nomes'] = [h['nome'] for h in demanda['habilidades']]
        demanda['habilidades_requeridas'] = ", ".join(demanda['habilidades_nomes'])
        
        return demanda

