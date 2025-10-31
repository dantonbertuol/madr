import re


def sanitize_string(string: str) -> str:
    """
    Sanitiza uma string removendo espaços extras, convertendo para minúsculas e removendo pontuação.

    Args:
        string (str): A string a ser sanitizada.

    Returns:
        str: A string sanitizada.
    """
    # Remove pontuação
    if string:
        result = re.sub(r"[^\w\s]", "", string)
        # Remove espaços extras e converte para minúsculas
        result = " ".join(result.split()).lower()
        return result
    return string


def auth_error() -> dict:
    """
    Retorna uma mensagem de erro de autenticação padrão.

    Returns:
        dict: A mensagem de erro de autenticação.
    """
    return {"message": "Email ou senha incorretos"}


def permission_error() -> dict:
    """
    Retorna uma mensagem de erro de permissão padrão.

    Returns:
        dict: A mensagem de erro de permissão.
    """
    return {"message": "Não autorizado"}


def not_found_error(entity: str) -> dict:
    """
    Retorna uma mensagem de erro de não encontrado padrão.

    Args:
        entity (str): O nome da entidade que não foi encontrada.

    Returns:
        str: A mensagem de erro de não encontrado.
    """
    return {"message": f"{entity.capitalize()} não consta no MADR"}


def conflict_error(entity: str) -> dict:
    """
    Retorna uma mensagem de erro de conflito padrão.

    Args:
        entity (str): O nome da entidade que está em conflito.

    Returns:
        str: A mensagem de erro de conflito.
    """
    return {"message": f"{entity.capitalize()} já consta no MADR"}


def deleted_message(entity: str) -> dict:
    """
    Retorna uma mensagem de confirmação de remoção padrão.

    Args:
        entity (str): O nome da entidade que foi removida.

    Returns:
        str: A mensagem de confirmação de remoção.
    """
    return {"message": f"{entity.capitalize()} deleted"}
