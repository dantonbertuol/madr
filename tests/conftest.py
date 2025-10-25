from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from madr.models import Romancista, table_registry


@pytest.fixture(scope="session")
def engine():
    with PostgresContainer("postgres:16", driver="psycopg") as postgres:
        _engine = create_async_engine(postgres.get_connection_url())
        yield _engine


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        # run_sync executa de forma síncrona a função
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def romancista(session):
    romancista = Romancista(nome="Autor Teste")

    session.add(romancista)
    await session.commit()
    await session.refresh(romancista)

    return romancista


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 8, 3)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, "created_at"):
            target.created_at = time
        if hasattr(target, "updated_at"):
            target.updated_at = time

    event.listen(model, "before_insert", fake_time_hook)

    yield time

    event.remove(model, "before_insert", fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time
