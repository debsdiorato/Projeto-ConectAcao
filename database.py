"""Módulo de banco de dados - SQLite com segurança."""
import sqlite3
from contextlib import contextmanager

DB_FILE = "voluntarios.db"


def migrar_banco():
    """Migra banco de dados antigo para nova estrutura."""
    conn = sqlite3.connect(DB_FILE) #abre conexao com o banco
    cursor = conn.cursor() #cria o tal do cursor
    
    try: #tente fazer né
        # Verificar se a tabela demandas existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='demandas'") #faz um select no sqlete_master, uma tabela interna do sqlite, para verificar a existencia de uma tabela demandas
        if cursor.fetchone(): #pega a primeira linha do resultado
            cursor.execute("PRAGMA table_info(demandas)") #pega informacoes da tabela demandas
            colunas = [row[1] for row in cursor.fetchall()] #cria uma lista com todos os nomes de coluna da tabela
            
            if 'habilidades_requeridas' in colunas: #verifica se existe um acoluna chamada habilidades_requiridas, se existe a tabela ta na versao antiga
                try: #outro bloco de tentaiva, agora só para salvar os dados antigos
                    cursor.execute("SELECT id, titulo FROM demandas") #pega todos os campos id e titulo da tabela antiga
                    dados_antigos = cursor.fetchall() #guarda todos os dados na variavel
                except:
                    dados_antigos = [] #assume que nao há dados (pra n dar merda no programa)
                
                # Remover tabelas antigas
                cursor.execute("DROP TABLE IF EXISTS demanda_habilidades") #apaga a tabela demanda_habilidades caso exista
                cursor.execute("DROP TABLE IF EXISTS demandas") #apaga a tabela demanda se ela existir
                
                cursor.execute("""
                    CREATE TABLE demandas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        titulo TEXT NOT NULL,
                        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """) #recria a tabela demandas, sem o demanda_habilidade
                
                for row in dados_antigos: #percorre cada linha salva da tabela antiga
                    cursor.execute(
                        "INSERT INTO demandas (id, titulo) VALUES (?, ?)",
                        (row[0], row[1]) #insire cada registro na tabela antiga
                    )
                
                conn.commit() #confirmar as alteracoes feitas né
    except Exception as e:
        # Se der erro, tenta continuar
        conn.rollback()
    finally:
        conn.close() #fecha conexao com o banco sempre


def init_db():
    """Inicializa o banco de dados criando as tabelas necessárias."""
    migrar_banco() #antes de criar as novas tabelas ele chama a funcao, para gatantir que as tabelas eantigas se ajustem ao novo formato
    
    with get_connection() as conn:
        cursor = conn.cursor() #cursor de novo
        
        # Tabela de habilidades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habilidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL
            )
        """) #cria a tanela caso n exista, identificador unico, nome da habilidade nao pode repitir, nem ser nulo
        
        # Tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                papel TEXT DEFAULT 'voluntario' CHECK(papel IN ('voluntario', 'admin'))
            )
        """) #email unico, senha criptografada, check para só aceitar voluntarios e adms,valor padrao usuario
        
        # Tabela de voluntários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voluntarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                disponibilidade TEXT,
                cidade TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """) #informaçoes estras dos voluntarios, cada usuario linkado via usuario_id, caso o usuario seja deletado o voluntario tambem é
        
        # Tabela de relação voluntário-habilidades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voluntario_habilidades (
                voluntario_id INTEGER NOT NULL,
                habilidade_id INTEGER NOT NULL,
                PRIMARY KEY (voluntario_id, habilidade_id),
                FOREIGN KEY (voluntario_id) REFERENCES voluntarios(id) ON DELETE CASCADE,
                FOREIGN KEY (habilidade_id) REFERENCES habilidades(id) ON DELETE CASCADE
            )
        """) #inpede que um voluntario tenha a mesma habilidade duas vezes, se o voluntario ou habilidade sumirem o registro é apagado
        
        # Tabela de demandas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demandas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """) #titulo obrigatorio, recebe a data atual automaticamente
        
        # Tabela de relação demanda-habilidades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demanda_habilidades (
                demanda_id INTEGER NOT NULL,
                habilidade_id INTEGER NOT NULL,
                PRIMARY KEY (demanda_id, habilidade_id),
                FOREIGN KEY (demanda_id) REFERENCES demandas(id) ON DELETE CASCADE,
                FOREIGN KEY (habilidade_id) REFERENCES habilidades(id) ON DELETE CASCADE
            )
        """) #relaciona demandas e habilidades necessarias, (on delete cascade garante a integridade)
        
        conn.commit() #salva tudo no banco
        
        #habilidades padrão
        popular_habilidades_padrao()


@contextmanager #transfroma a funcao em um gerenciador de contexto (para usar com 'with')
def get_connection():
    """Context manager para conexões seguras com o banco."""
    conn = sqlite3.connect(DB_FILE) #conecta no banco
    conn.row_factory = sqlite3.Row #tranfroma rows em objetos que se comportam como dicionarios
    conn.execute("PRAGMA foreign_keys = ON") #ativa foreign_keys, que no sqllite n vem ativa
    try:
        yield conn #entrega a conexao para ser usando dentro do bloco with
        conn.commit() #salva se n tiver erro
    except Exception:
        conn.rollback() #desfaz as cagadas
        raise #raise para realcar o erro
    finally:
        conn.close() #sempre fecha a conexao


def criar_usuario(nome, email, senha_hash, papel='voluntario'):
    """Cria um novo usuário."""
    with get_connection() as conn: #abre conexao segura com o banco
        cursor = conn.cursor() #curor de novo
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, papel) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, papel)
        ) #insere as cinformacoes do usuario no banco
        return cursor.lastrowid #retorna o id do novo usuario


def buscar_usuario_por_email(email):
    """Busca usuário por email."""
    with get_connection() as conn: #abre conexao segura
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,)) #pega todas as colunas e filtra por e-mail
        row = cursor.fetchone()#pega a primeira linha encontrada
        return dict(row) if row else None # se row existe trnaformna em um dicionario pyton, se nao é none


def popular_habilidades_padrao():
    """Popula o banco com habilidades padrão."""
    habilidades_padrao = [
        "Engenharia", "Marketing", "Pedreiro", "Enfermagem", "Educação",
        "Design", "Programação", "Contabilidade", "Advocacia", "Medicina",
        "Psicologia", "Arquitetura", "Jornalismo", "Fotografia", "Culinária",
        "Música", "Artes", "Esportes", "Idiomas", "Administração"
    ]#contem todas as habilidades que sarao criadas automaticamente quando inicializar o banco, cada item vira uma linha na tabela
    
    with get_connection() as conn: #abre conexao com o banco
        cursor = conn.cursor() #cursor de novo
        for hab in habilidades_padrao: #loop para passar todas as habilidades
            try: #try para caso de erro ele continue inserindo as habilidades
                cursor.execute("INSERT OR IGNORE INTO habilidades (nome) VALUES (?)", (hab,)) #tenta inserir a habilidade na lista, caso ja exista ele ignora
            except:
                pass
        conn.commit() #salva as paradas


def listar_habilidades():
    """Lista todas as habilidades disponíveis."""
    with get_connection() as conn: #abre a conexao com o banco
        cursor = conn.cursor() #cursor novamente
        cursor.execute("SELECT * FROM habilidades ORDER BY nome") #puxa todas as habilidades cadastradas no banco
        return [dict(row) for row in cursor.fetchall()] #pega todas as linhas, tranforma em um dicionário e devolve elas como lista


def criar_voluntario(usuario_id, habilidades_ids, disponibilidade="", cidade=""):
    """Cria perfil de voluntário com habilidades."""
    with get_connection() as conn: #conexao com banco
        cursor = conn.cursor() 
        cursor.execute(
            "INSERT INTO voluntarios (usuario_id, disponibilidade, cidade) VALUES (?, ?, ?)",
            (usuario_id, disponibilidade, cidade) 
        ) #insere um novo usuario com id, disponibilidade e cidade
        voluntario_id = cursor.lastrowid #pega o id no novo voluntario
        
        # Adicionar habilidades
        for hab_id in habilidades_ids: #loop para chegar na habilidade selecionada
            cursor.execute(
                "INSERT INTO voluntario_habilidades (voluntario_id, habilidade_id) VALUES (?, ?)",
                (voluntario_id, hab_id) #insere a habilidade na tabela de relaçao
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

