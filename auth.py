"""Módulo de autenticação e segurança."""  # Docstring do módulo
import os  # Importa o módulo os para acessar variáveis de ambiente
import re  # Importa o módulo re para operações com expressões regulares
from werkzeug.security import generate_password_hash, check_password_hash  # Importa funções de hash de senha do werkzeug
from dotenv import load_dotenv  # Importa a função load_dotenv para carregar variáveis de ambiente do arquivo .env

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

# Credenciais do admin (apenas do .env)
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")  # Obtém o email do administrador das variáveis de ambiente
ADMIN_SENHA = os.getenv("ADMIN_SENHA")  # Obtém a senha do administrador das variáveis de ambiente
ADMIN_NOME = os.getenv("ADMIN_NOME", "Administrador")  # Obtém o nome do administrador das variáveis de ambiente, com valor padrão "Administrador"


def validar_email(email):
    """
    Valida formato de email rigoroso.
    Formato esperado: pedro@hostdousuário.com
    """
    if not email:  # Verifica se o email está vazio
        return False, "Email não pode estar vazio"  # Retorna False e mensagem de erro se o email estiver vazio
    
    # Padrão regex para email válido
    # Formato: nome@dominio.extensao
    # - Nome: letras, números, pontos, hífens, underscores
    # - Domínio: letras, números, hífens, pontos
    # - Extensão: pelo menos 2 letras
    padrao = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'  # Define o padrão regex para validar formato de email
    
    if not re.match(padrao, email):  # Verifica se o email corresponde ao padrão regex
        return False, "Email inválido. Use o formato: nome@dominio.com"  # Retorna False e mensagem de erro se não corresponder
    
    # Verificações adicionais
    partes = email.split('@')  # Divide o email pelo caractere @
    if len(partes) != 2:  # Verifica se há exatamente duas partes (antes e depois do @)
        return False, "Email deve conter exatamente um @"  # Retorna False e mensagem de erro se não houver exatamente um @
    
    nome_usuario = partes[0]  # Obtém a parte antes do @ (nome de usuário)
    dominio_completo = partes[1]  # Obtém a parte depois do @ (domínio completo)
    
    # Validar nome de usuário
    if len(nome_usuario) < 1:  # Verifica se o nome de usuário tem pelo menos 1 caractere
        return False, "Nome de usuário do email não pode estar vazio"  # Retorna False e mensagem de erro se estiver vazio
    
    if nome_usuario.startswith('.') or nome_usuario.endswith('.'):  # Verifica se o nome de usuário começa ou termina com ponto
        return False, "Nome de usuário não pode começar ou terminar com ponto"  # Retorna False e mensagem de erro se começar ou terminar com ponto
    
    # Validar domínio
    if '.' not in dominio_completo:  # Verifica se o domínio contém pelo menos um ponto
        return False, "Domínio deve conter pelo menos um ponto (ex: dominio.com)"  # Retorna False e mensagem de erro se não houver ponto
    
    partes_dominio = dominio_completo.split('.')  # Divide o domínio pelos pontos
    if len(partes_dominio) < 2:  # Verifica se há pelo menos duas partes no domínio
        return False, "Domínio inválido"  # Retorna False e mensagem de erro se o domínio for inválido
    
    extensao = partes_dominio[-1]  # Obtém a última parte do domínio (extensão)
    if len(extensao) < 2:  # Verifica se a extensão tem pelo menos 2 caracteres
        return False, "Extensão do domínio deve ter pelo menos 2 caracteres"  # Retorna False e mensagem de erro se a extensão for muito curta
    
    return True, "Email válido"  # Retorna True e mensagem de sucesso se todas as validações passarem


def validar_senha_forte(senha):
    """
    Valida se a senha atende aos critérios de segurança:
    - Pelo menos uma letra maiúscula
    - Pelo menos um número
    - Pelo menos um caractere especial
    - Mínimo de 8 caracteres
    """
    if not senha:  # Verifica se a senha está vazia
        return False, "Senha não pode estar vazia"  # Retorna False e mensagem de erro se a senha estiver vazia
    
    erros = []  # Cria uma lista vazia para armazenar os erros encontrados
    
    # Verificar comprimento mínimo
    if len(senha) < 8:  # Verifica se a senha tem menos de 8 caracteres
        erros.append("A senha deve ter pelo menos 8 caracteres")  # Adiciona erro à lista se a senha for muito curta
    
    # Verificar letra maiúscula
    if not re.search(r'[A-Z]', senha):  # Verifica se a senha contém pelo menos uma letra maiúscula
        erros.append("A senha deve conter pelo menos uma letra maiúscula")  # Adiciona erro à lista se não houver letra maiúscula
    
    # Verificar número
    if not re.search(r'[0-9]', senha):  # Verifica se a senha contém pelo menos um número
        erros.append("A senha deve conter pelo menos um número")  # Adiciona erro à lista se não houver número
    
    # Verificar caractere especial
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|,.<>/?]', senha):  # Verifica se a senha contém pelo menos um caractere especial
        erros.append("A senha deve conter pelo menos um caractere especial (!@#$%^&*()_+-=[]{};':\"|,.<>/? etc)")  # Adiciona erro à lista se não houver caractere especial
    
    if erros:  # Verifica se há erros na lista
        mensagem = "A senha não atende aos critérios de segurança:\n" + "\n".join(f"• {erro}" for erro in erros)  # Cria mensagem formatada com todos os erros
        return False, mensagem  # Retorna False e a mensagem com todos os erros
    
    return True, "Senha válida"  # Retorna True e mensagem de sucesso se todas as validações passarem


def hash_senha(senha):
    """Gera hash seguro da senha usando PBKDF2."""  # Docstring da função
    return generate_password_hash(senha, method='pbkdf2:sha256')  # Gera e retorna o hash da senha usando o método PBKDF2 com SHA256


def verificar_senha(senha_hash, senha):
    """Verifica se a senha corresponde ao hash."""  # Docstring da função
    return check_password_hash(senha_hash, senha)  # Verifica se a senha fornecida corresponde ao hash e retorna True ou False


def verificar_admin(email, senha):
    """Verifica se as credenciais são do admin do .env."""  # Docstring da função
    if not ADMIN_EMAIL or not ADMIN_SENHA:  # Verifica se as credenciais do admin não estão configuradas
        return False  # Retorna False se as credenciais não estiverem configuradas
    return email == ADMIN_EMAIL and senha == ADMIN_SENHA  # Retorna True se o email e senha corresponderem às credenciais do admin


def get_admin_info():
    """Retorna informações do admin se configurado."""  # Docstring da função
    if ADMIN_EMAIL and ADMIN_SENHA:  # Verifica se as credenciais do admin estão configuradas
        return {  # Retorna um dicionário com as informações do admin
            'id': 0,  # Define o ID do admin como 0
            'nome': ADMIN_NOME,  # Define o nome do admin
            'email': ADMIN_EMAIL,  # Define o email do admin
            'papel': 'admin'  # Define o papel do admin
        }
    return None  # Retorna None se as credenciais do admin não estiverem configuradas

