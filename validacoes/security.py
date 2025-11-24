from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(senha: str) -> str:
    """Gera hash seguro da senha para armazenar."""
    return generate_password_hash(senha)

def verify_password(senha_hash: str, senha: str) -> bool:
    """Verifica senha informada contra o hash armazenado."""
    return check_password_hash(senha_hash, senha)