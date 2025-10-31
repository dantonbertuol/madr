from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database import get_session
from madr.models import Romancista
from madr.routers.contas import CurrentUser
from madr.schemas import FilterRomancista, Message, RomancistaList, RomancistaPublic, RomancistaSchema, RomancistaUpdate
from madr.utils import conflict_error, not_found_error, sanitize_string

router = APIRouter(prefix="/romancista", tags=["romancista"])


Session = Annotated[AsyncSession, Depends(get_session)]

ENTITY: str = "Romancista"


@router.post("/", status_code=HTTPStatus.CREATED, response_model=RomancistaPublic)
async def create_romancista(romancista: RomancistaSchema, session: Session, user: CurrentUser):
    romancista.nome = sanitize_string(romancista.nome)
    db_romancista = await session.scalar(select(Romancista).where((Romancista.nome == romancista.nome)))

    if db_romancista:
        if db_romancista.nome == romancista.nome:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=conflict_error(ENTITY),
            )

    db_romancista = Romancista(nome=romancista.nome)
    session.add(db_romancista)
    await session.commit()
    await session.refresh(db_romancista)

    return db_romancista


@router.get("/{id}", status_code=HTTPStatus.OK, response_model=RomancistaPublic)
async def read_romancista(id: int, session: Session):
    romancista = await session.scalar(select(Romancista).where(Romancista.id == id))
    if not romancista:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=not_found_error(ENTITY))

    return romancista


@router.get("/", status_code=HTTPStatus.OK, response_model=RomancistaList)
async def read_romancistas_by_name(filter_romancistas: Annotated[FilterRomancista, Query()], session: Session):
    stmt = select(Romancista).offset(filter_romancistas.offset).limit(filter_romancistas.limit)
    if filter_romancistas.nome:
        name = sanitize_string(filter_romancistas.nome)
        stmt = stmt.where(Romancista.nome.ilike(f"%{name}%"))
    query = await session.scalars(stmt)
    romancistas = query.all()
    return {"romancistas": romancistas}


@router.patch("/{id}", response_model=RomancistaPublic)
async def update_romancista(id: int, romancista: RomancistaUpdate, session: Session, user: CurrentUser):
    db_romancista = await session.scalar(select(Romancista).where((Romancista.id == id)))

    if not db_romancista:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=not_found_error(ENTITY))

    if romancista.nome:
        romancista.nome = sanitize_string(romancista.nome)

    romancista_by_name = await session.scalar(select(Romancista).where((Romancista.nome) == romancista.nome))

    if romancista_by_name:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=conflict_error(ENTITY),
        )

    for key, value in romancista.model_dump(exclude_unset=True).items():
        setattr(db_romancista, key, value)

    session.add(db_romancista)
    await session.commit()
    await session.refresh(db_romancista)

    return db_romancista


@router.delete("/{id}", response_model=Message)
async def delete_romancista(id: int, session: Session, user: CurrentUser):
    db_romancista = await session.scalar(select(Romancista).where((Romancista.id == id)))
    if not db_romancista:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=not_found_error(ENTITY))

    await session.delete(db_romancista)

    await session.commit()

    return {"message": "Romancista deleted"}
