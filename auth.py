"""Módulo de autenticação e segurança."""
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

# Credenciais do admin (apenas do .env)
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_SENHA = os.getenv("ADMIN_SENHA")
ADMIN_NOME = os.getenv("ADMIN_NOME", "Administrador")


def validar_email(email):
    """
    Valida formato de email rigoroso.
    Formato esperado: pedro@hostdousuário.com
    """
    if not email:
        return False, "Email não pode estar vazio"
    
    # Padrão regex para email válido
    # Formato: nome@dominio.extensao
    # - Nome: letras, números, pontos, hífens, underscores
    # - Domínio: letras, números, hífens, pontos
    # - Extensão: pelo menos 2 letras
    padrao = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(padrao, email):
        return False, "Email inválido. Use o formato: nome@dominio.com"
    
    # Verificações adicionais
    partes = email.split('@')
    if len(partes) != 2:
        return False, "Email deve conter exatamente um @"
    
    nome_usuario = partes[0]
    dominio_completo = partes[1]
    
    # Validar nome de usuário
    if len(nome_usuario) < 1:
        return False, "Nome de usuário do email não pode estar vazio"
    
    if nome_usuario.startswith('.') or nome_usuario.endswith('.'):
        return False, "Nome de usuário não pode começar ou terminar com ponto"
    
    # Validar domínio
    if '.' not in dominio_completo:
        return False, "Domínio deve conter pelo menos um ponto (ex: dominio.com)"
    
    partes_dominio = dominio_completo.split('.')
    if len(partes_dominio) < 2:
        return False, "Domínio inválido"
    
    extensao = partes_dominio[-1]
    if len(extensao) < 2:
        return False, "Extensão do domínio deve ter pelo menos 2 caracteres"
    
    return True, "Email válido"


def validar_senha_forte(senha):
    """
    Valida se a senha atende aos critérios de segurança:
    - Pelo menos uma letra maiúscula
    - Pelo menos um número
    - Pelo menos um caractere especial
    - Mínimo de 8 caracteres
    """
    if not senha:
        return False, "Senha não pode estar vazia"
    
    erros = []
    
    # Verificar comprimento mínimo
    if len(senha) < 8:
        erros.append("A senha deve ter pelo menos 8 caracteres")
    
    # Verificar letra maiúscula
    if not re.search(r'[A-Z]', senha):
        erros.append("A senha deve conter pelo menos uma letra maiúscula")
    
    # Verificar número
    if not re.search(r'[0-9]', senha):
        erros.append("A senha deve conter pelo menos um número")
    
    # Verificar caractere especial
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|,.<>/?]', senha):
        erros.append("A senha deve conter pelo menos um caractere especial (!@#$%^&*()_+-=[]{};':\"|,.<>/? etc)")
    
    if erros:
        mensagem = "A senha não atende aos critérios de segurança:\n" + "\n".join(f"• {erro}" for erro in erros)
        return False, mensagem
    
    return True, "Senha válida"


def hash_senha(senha):
    """Gera hash seguro da senha usando PBKDF2."""
    return generate_password_hash(senha, method='pbkdf2:sha256')


def verificar_senha(senha_hash, senha):
    """Verifica se a senha corresponde ao hash."""
    return check_password_hash(senha_hash, senha)


def verificar_admin(email, senha):
    """Verifica se as credenciais são do admin do .env."""
    if not ADMIN_EMAIL or not ADMIN_SENHA:
        return False
    return email == ADMIN_EMAIL and senha == ADMIN_SENHA


def get_admin_info():
    """Retorna informações do admin se configurado."""
    if ADMIN_EMAIL and ADMIN_SENHA:
        return {
            'id': 0,
            'nome': ADMIN_NOME,
            'email': ADMIN_EMAIL,
            'papel': 'admin'
        }
    return None

