from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database import get_session
from madr.models import Romancista
from madr.schemas import FilterPage, Message, RomancistaList, RomancistaPublic, RomancistaSchema

router = APIRouter(prefix="/romancistas", tags=["romancistas"])


Session = Annotated[AsyncSession, Depends(get_session)]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=RomancistaPublic)
async def create_romancista(romancista: RomancistaSchema, session: Session):
    db_romancista = await session.scalar(select(Romancista).where((Romancista.nome == romancista.nome)))

    if db_romancista:
        if db_romancista.nome == romancista.nome:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Romancista already exists",
            )

    db_romancista = Romancista(nome=romancista.nome)
    session.add(db_romancista)
    await session.commit()
    await session.refresh(db_romancista)

    return db_romancista


@router.get("/", response_model=RomancistaList)
async def read_romancistas(filter_romancistas: Annotated[FilterPage, Query()], session: Session):
    query = await session.scalars(select(Romancista).offset(filter_romancistas.offset).limit(filter_romancistas.limit))
    romancistas = query.all()
    return {"romancistas": romancistas}


@router.get("/{romancista_id}", status_code=HTTPStatus.OK, response_model=RomancistaPublic)
async def read_romancista(romancista_id: int, session: Session):
    romancista = await session.scalar(select(Romancista).where(Romancista.id == romancista_id))
    if not romancista:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Romancista not found")

    return romancista


@router.patch("/{romancista_id}", response_model=RomancistaPublic)
async def update_romancista(
    romancista_id: int,
    romancista: RomancistaSchema,
    session: Session,
):
    db_romancista = await session.scalar(select(Romancista).where((Romancista.id == romancista_id)))

    if not db_romancista:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Romancista not found.")

    romancista_by_name = await session.scalar(select(Romancista).where((Romancista.nome) == romancista.nome))

    if romancista_by_name:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Romancista already exists",
        )

    for key, value in romancista.model_dump(exclude_unset=True).items():
        setattr(db_romancista, key, value)

    session.add(db_romancista)
    await session.commit()
    await session.refresh(db_romancista)

    return db_romancista


@router.delete("/{romancista_id}", response_model=Message)
async def delete_user(
    romancista_id: int,
    session: Session,
):
    db_romancista = await session.scalar(select(Romancista).where((Romancista.id == romancista_id)))
    if not db_romancista:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Romancista not found.")

    await session.delete(db_romancista)

    await session.commit()

    return {"message": "Romancista deleted"}
