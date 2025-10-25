from dataclasses import asdict

import pytest
from sqlalchemy import select

from madr.models import Livro, Romancista, User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(username="alice", senha="secret", email="teste@test")
        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == "alice"))

    assert asdict(user) == {
        "id": 1,
        "username": "alice",
        "senha": "secret",
        "email": "teste@test",
        "created_at": time,
        "updated_at": time,
    }


@pytest.mark.asyncio
async def test_create_romancista(session, mock_db_time):
    with mock_db_time(model=Romancista) as time:
        romancista = Romancista(
            nome="Test Romancista",
        )
        session.add(romancista)
        await session.commit()

    romancista = await session.scalar(select(Romancista).where(Romancista.nome == "Test Romancista"))

    assert asdict(romancista) == {
        "id": 1,
        "nome": "Test Romancista",
        "created_at": time,
        "updated_at": time,
        "livros": [],
    }


@pytest.mark.asyncio
async def test_create_livro(session, romancista, mock_db_time):
    with mock_db_time(model=Livro) as time:
        livro = Livro(
            titulo="Test Livro",
            ano=2023,
            id_romancista=romancista.id,
        )
        session.add(livro)
        await session.commit()

    livro = await session.scalar(select(Livro).where(Livro.titulo == "Test Livro"))

    assert asdict(livro) == {
        "id": 1,
        "ano": 2023,
        "titulo": "Test Livro",
        "id_romancista": romancista.id,
        "romancista": asdict(romancista),
        "created_at": time,
        "updated_at": time,
    }


@pytest.mark.asyncio
async def test_romancista_livro_relation(session, romancista: Romancista):
    livro = Livro(
        titulo="Test Livro",
        ano=2023,
        id_romancista=romancista.id,
    )

    session.add(livro)
    await session.commit()
    await session.refresh(romancista)

    romancista = await session.scalar(select(Romancista).where(Romancista.id == romancista.id))

    assert romancista.livros == [livro]
