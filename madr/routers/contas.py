from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database import get_session
from madr.models import User
from madr.schemas import (
    Message,
    Token,
    UserPublic,
    UserSchema,
)
from madr.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from madr.utils import auth_error, deleted_message, permission_error, sanitize_string

router = APIRouter(prefix="/conta", tags=["conta"])


Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]

ENTITY: str = "User"


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: Session):
    """
    Cria um novo usuário no banco de dados após validar que o username e o email são únicos.

    Args:
        user (UserSchema): Dados do usuário contendo username, email e senha.
        session (Session): Sessão do banco utilizada para consultas e commits.

    Returns:
        User: O objeto do usuário recém-criado.

    Raises:
        HTTPException: Se o username ou email já existir no banco de dados.
    """
    user.username = sanitize_string(user.username)
    db_user = await session.scalar(select(User).where((User.username == user.username) | (User.email == user.email)))

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Username already exists",
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Email already exists",
            )

    hashed_password = get_password_hash(user.senha)

    db_user = User(
        email=user.email,
        username=user.username,
        senha=hashed_password,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.put("/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    current_user: CurrentUser,
    session: Session,
):
    """
    Atualiza os dados de um usuário existente, permitindo alteração de username, email e senha.

    Args:
        user_id (int): ID do usuário a ser atualizado.
        user (UserSchema): Novos dados do usuário.
        current_user (User): Usuário autenticado realizando a operação.
        session (Session): Sessão do banco utilizada para persistência.

    Returns:
        User: O objeto do usuário atualizado.

    Raises:
        HTTPException: Se o usuário autenticado não for o mesmo do user_id ou se username/email já existirem.
    """
    user.username = sanitize_string(user.username)
    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=permission_error())

    try:
        current_user.username = user.username
        current_user.senha = get_password_hash(user.senha)
        current_user.email = user.email
        await session.commit()
        await session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Username or Email already exists")


@router.delete("/{user_id}", response_model=Message)
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    session: Session,
):
    """
    Remove um usuário do banco de dados, caso o usuário autenticado seja o mesmo do user_id.

    Args:
        user_id (int): ID do usuário a ser removido.
        current_user (User): Usuário autenticado realizando a operação.
        session (Session): Sessão do banco utilizada para persistência.

    Returns:
        dict: Mensagem de confirmação da remoção.

    Raises:
        HTTPException: Se o usuário autenticado não for o mesmo do user_id.
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=permission_error())

    await session.delete(current_user)

    await session.commit()

    return deleted_message(ENTITY)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    session: Session,
    form_data: OAuth2Form,
):
    """
    Realiza o login do usuário e retorna um token de acesso JWT.

    Args:
        session (Session): Sessão do banco utilizada para consulta do usuário.
        form_data (OAuth2PasswordRequestForm): Dados de autenticação (email e senha).

    Returns:
        dict: Token de acesso e tipo do token.

    Raises:
        HTTPException: Se o usuário não existir ou a senha estiver incorreta.
    """
    user = await session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=auth_error())

    if not verify_password(form_data.password, user.senha):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=auth_error())

    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh_token", response_model=Token)
async def refresh_access_token(user: CurrentUser):
    """
    Gera um novo token de acesso JWT para o usuário autenticado.

    Args:
        user (User): Usuário autenticado.

    Returns:
        dict: Novo token de acesso e tipo do token.
    """
    new_access_token = create_access_token(data={"sub": user.email})

    return {"access_token": new_access_token, "token_type": "bearer"}
