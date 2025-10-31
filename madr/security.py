from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database import get_session
from madr.models import User
from madr.settings import Settings

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="conta/token")


settings = Settings()


def create_access_token(data: dict) -> str:
    """
    Cria um token JWT com os dados fornecidos e uma data de expiração.

    Args:
        data (dict): Dados a serem incluídos no token.

    Returns:
        str: O token JWT codificado.
    """
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_password_hash(password: str) -> str:
    """
    Gera um hash seguro para a senha fornecida.

    Args:
        password (str): A senha em texto plano.

    Returns:
        str: O hash da senha.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash fornecido.

    Args:
        plain_password (str): A senha em texto plano.
        hashed_password (str): O hash da senha para verificação.

    Returns:
        bool: True se a senha corresponder ao hash, False caso contrário.
    """
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    """
    Obtém o usuário atual com base no token JWT fornecido.

    Args:
        session (AsyncSession): Sessão do banco de dados.
        token (str): Token JWT do usuário autenticado.
    Returns:
        User: O objeto do usuário autenticado.
    Raises:
        HTTPException: Se o token for inválido ou o usuário não for encontrado.
    """
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject_email = payload.get("sub")

        if not subject_email:
            raise credentials_exception

    except (DecodeError, ExpiredSignatureError):
        raise credentials_exception

    user = await session.scalar(select(User).where(User.email == subject_email))

    if not user:
        raise credentials_exception

    return user
