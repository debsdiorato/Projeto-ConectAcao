# database.py
import sqlite3

DB = "voluntarios.db"

def get_conn():
    """Abre conexão com o banco SQLite."""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# ---------------- USUÁRIOS ---------------- #

def criar_usuario(nome, telefone, email, senha_hash, papel="voluntario"):
    conn = get_conn() #conecta no banco
    cur = conn.cursor() #abre um cursor pra sql
    cur.execute("""
        INSERT INTO usuarios (nome, telefone, email, senha_hash, papel)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, telefone, email, senha_hash, papel)) #insire um novo usuario (? pra evitar sql injection)
    conn.commit() #salva mudancas
    uid = cur.lastrowid #pega id do usuario novo
    conn.close() #fecha conexao
    return uid #retorna o id do novo usario

def buscar_usuario_por_email(email):
    conn = get_conn() #conecta no banco
    cur = conn.cursor() #abre cursos de novo
    cur.execute("SELECT * FROM usuarios WHERE email = ?", (email,)) #procura o usuario pelo email
    row = cur.fetchone() #pra pegar só 1 usuario
    conn.close() #fecha
    return dict(row) if row else None #se n achar retorna None

# ---------------- VOLUNTÁRIOS ---------------- #

def criar_voluntario(usuario_id, habilidades, disponibilidade, cidade): #pega o id do usuario, coleta as habilidades, cidade e disponibilidade
    conn = get_conn() #conecta no banco
    cur = conn.cursor()#cursor
    cur.execute("""
        INSERT INTO voluntarios (usuario_id, habilidades, disponibilidade, cidade)
        VALUES (?, ?, ?, ?)
    """, (usuario_id, habilidades, disponibilidade, cidade)) #insere no banco as paradas
    conn.commit()
    conn.close()

def atualizar_voluntario(usuario_id, habilidades, disponibilidade, cidade): #pra caso o usuario queria atualizar seu perfil de voluntario
    conn = get_conn() #conecta no banco
    cur = conn.cursor()
    cur.execute("""
        UPDATE voluntarios
        SET habilidades = ?, disponibilidade = ?, cidade = ?
        WHERE usuario_id = ?
    """, (habilidades, disponibilidade, cidade, usuario_id))
    conn.commit() #salva
    conn.close()

def listar_voluntarios():
    conn = get_conn() #chama a funcao la
    cur = conn.cursor() #cria cursor
    cur.execute("""
        SELECT v.*, u.nome, u.email, u.telefone
        FROM voluntarios v
        JOIN usuarios u ON u.id = v.usuario_id
    """) #Select para pegar tudo na tabela voluntarios, e o nome, email e telefone da tabela usuarios
        #join para combiar o voluntario com o usuario, o v.usuario_id é o campo dentro de voluntarios que garda qual usuario é dono daquele id
        #em resumo, pega as informaçoes de todos os voluntarios, o nome, e-mail e telefone deles, usando a chave id_user
    rows = cur.fetchall() #pega todos os resultados das linhas do select e coloca no rows
    conn.close()
    return [dict(r) for r in rows] #tranforma cada linha em um dicionario, para facilitar a vida

# ---------------- DEMANDAS (SUPER SIMPLES) ---------------- #

def criar_demanda(titulo, habilidades_requeridas):
    conn = get_conn() #def de conectar la
    cur = conn.cursor() #cursor de novo
    cur.execute("""
        INSERT INTO demandas (titulo, habilidades_requeridas)
        VALUES (?, ?)
    """, (titulo, habilidades_requeridas)) #Insere as paradas na tabela demandas
    conn.commit() #crtl s da vida
    d_id = cur.lastrowid #cria o id da demanda
    conn.close()#fecha por boas praticas
    return d_id #retorna o id da demanda

def listar_demandas(): #funcao ai de listar demandas😊
    conn = get_conn() #funcao de novo
    cur = conn.cursor() #cursos ai de novo
    cur.execute("SELECT * FROM demandas") #select das demandas, pra pegar todas as demandas
    rows = cur.fetchall() #pega TODAS as demandas e coloca dentro da lista rows
    conn.close() #fecha por boas praticas😂😂😂
    return [dict(r) for r in rows] #converte cada linha para um dicionario pyton

def buscar_demanda_por_id(demanda_id): #busca a demanda pelo id dela
    conn = get_conn()#olha ela ai de novo, a funcao mais querida do codigo
    cur = conn.cursor()#cursor
    cur.execute("SELECT * FROM demandas WHERE id = ?", (demanda_id,)) #procura a demanda pelo id, tem o ? por boas praticas de novo
    row = cur.fetchone() #fetchone para pegar apenas a primeira linha, porque so existe 1 id né
    conn.close()#fecha de novo
    return dict(row) if row else None #se achou algo retorna um dicionario, se n achou retorna None
