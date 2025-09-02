# core/validators.py

def campo_obrigatorio(valor: str, nome: str):
    if not valor.strip():
        return f"O campo '{nome}' é obrigatório."
    return None

def email_valido(email: str):
    import re
    padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(padrao, email.strip()):
        return "Email inválido."
    return None

def telefone_valido(telefone: str):
    if telefone and len(telefone.strip()) < 9:
        return "Telefone muito curto."
    return None