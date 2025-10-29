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
from madr.utils import auth_error, permission_error, sanitize_string

router = APIRouter(prefix="/conta", tags=["conta"])


Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: Session):
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
    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=permission_error())

    await session.delete(current_user)

    await session.commit()

    return {"message": "User deleted"}


@router.post("/token", response_model=Token)
async def login_for_access_token(
    session: Session,
    form_data: OAuth2Form,
):
    user = await session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=auth_error())

    if not verify_password(form_data.password, user.senha):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=auth_error())

    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh_token", response_model=Token)
async def refresh_access_token(user: CurrentUser):
    new_access_token = create_access_token(data={"sub": user.email})

    return {"access_token": new_access_token, "token_type": "bearer"}
