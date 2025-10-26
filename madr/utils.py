import re


def sanitize_string(string: str) -> str:
    # Remove pontuação
    result = re.sub(r"[^\w\s]", "", string)
    # Remove espaços extras e converte para minúsculas
    result = " ".join(result.split()).lower()
    return result


def auth_error() -> str:
    return {"message": "Email ou senha incorretos"}


def permission_error() -> str:
    return {"message": "Não autorizado"}


def not_found_error(entity: str) -> str:
    return {"message": f"{entity.capitalize()} não consta no MADR"}


def conflict_error(entity: str) -> str:
    return {"message": f"{entity.capitalize()} já consta no MADR"}
