from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from madr.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)


async def get_session():  # pragma: no cover
    # expire_on_commit não fecha a sessão após o commit, o que seria o padrão
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
