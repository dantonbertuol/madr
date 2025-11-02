from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database import get_session
from madr.models import Livro, Romancista
from madr.routers.contas import CurrentUser
from madr.schemas import FilterLivro, LivroList, LivroPublic, LivroSchema, LivroUpdate, Message
from madr.utils import conflict_error, deleted_message, not_found_error, sanitize_string

router = APIRouter(prefix="/livro", tags=["livro"])


Session = Annotated[AsyncSession, Depends(get_session)]

ENTITY: str = "Livro"


@router.post("/", status_code=HTTPStatus.CREATED, response_model=LivroPublic)
async def create_livro(livro: LivroSchema, session: Session, user: CurrentUser):
    """
    Cria um novo livro no banco de dados após validar que o título é único.

    Args:
        livro (LivroSchema): Dados do livro contendo título, ano e id do romancista.
        session (Session): Sessão do banco utilizada para consultas e commits.
        user (User): Usuário autenticado realizando a operação.

    Returns:
        Livro: O objeto do livro recém-criado.

    Raises:
        HTTPException: Se o título já existir no banco de dados.
    """
    livro.titulo = sanitize_string(livro.titulo)
    db_livro = await session.scalar(select(Livro).where((Livro.titulo == livro.titulo)))
    db_romancista = await session.scalar(select(Romancista).where(Romancista.id == livro.id_romancista))

    if not db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=not_found_error("Romancista"),
        )

    if db_livro:
        if db_livro.titulo == livro.titulo:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=conflict_error(ENTITY),
            )

    db_livro = Livro(titulo=livro.titulo, ano=livro.ano, id_romancista=livro.id_romancista)
    session.add(db_livro)
    await session.commit()
    await session.refresh(db_livro)

    return db_livro


@router.get("/{id}", status_code=HTTPStatus.OK, response_model=LivroPublic)
async def read_livro(id: int, session: Session):
    """
    Busca um livro pelo seu ID.

    Args:
        id (int): ID do livro a ser buscado.
        session (Session): Sessão do banco utilizada para consulta.

    Returns:
        Livro: O objeto do livro encontrado.

    Raises:
        HTTPException: Se o livro não for encontrado.
    """
    livro = await session.scalar(select(Livro).where(Livro.id == id))
    if not livro:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=not_found_error(ENTITY))

    return livro


@router.get("/", status_code=HTTPStatus.OK, response_model=LivroList)
async def read_livro_by_name_year(filter_livros: Annotated[FilterLivro, Query()], session: Session):
    """
    Busca livros filtrando por título parcial e/ou ano, com paginação.

    Args:
        filter_livros (FilterLivro): Filtros de busca (título, ano, offset, limit).
        session (Session): Sessão do banco utilizada para consulta.

    Returns:
        dict: Lista de livros encontrados.
    """
    stmt = select(Livro).offset(filter_livros.offset).limit(filter_livros.limit)

    if filter_livros.titulo:
        titulo = sanitize_string(filter_livros.titulo)
        stmt = stmt.where(Livro.titulo.ilike(f"%{titulo}%"))
    if filter_livros.ano:
        stmt = stmt.where(Livro.ano == filter_livros.ano)

    query = await session.scalars(stmt)
    livros = query.all()

    return {"livros": livros}


@router.patch("/{id}", response_model=LivroPublic)
async def update_livro(id: int, livro: LivroUpdate, session: Session, user: CurrentUser):
    """
    Atualiza os dados de um livro existente, permitindo alteração de título, ano e romancista.

    Args:
        id (int): ID do livro a ser atualizado.
        livro (LivroUpdate): Novos dados do livro.
        session (Session): Sessão do banco utilizada para persistência.
        user (User): Usuário autenticado realizando a operação.

    Returns:
        Livro: O objeto do livro atualizado.

    Raises:
        HTTPException: Se o livro não for encontrado ou se o título já existir.
    """
    db_livro = await session.scalar(select(Livro).where((Livro.id == id)))

    if not db_livro:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=not_found_error(ENTITY))

    if livro.titulo:
        livro.titulo = sanitize_string(livro.titulo)

    livro_by_titulo = await session.scalar(select(Livro).where((Livro.titulo) == livro.titulo))

    if livro_by_titulo:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=conflict_error(ENTITY),
        )

    for key, value in livro.model_dump(exclude_unset=True).items():
        setattr(db_livro, key, value)

    session.add(db_livro)
    await session.commit()
    await session.refresh(db_livro)

    return db_livro


@router.delete("/{id}", response_model=Message)
async def delete_livro(id: int, session: Session, user: CurrentUser):
    """
    Remove um livro do banco de dados pelo seu ID.

    Args:
        id (int): ID do livro a ser removido.
        session (Session): Sessão do banco utilizada para persistência.
        user (User): Usuário autenticado realizando a operação.

    Returns:
        dict: Mensagem de confirmação da remoção.

    Raises:
        HTTPException: Se o livro não for encontrado.
    """
    db_livro = await session.scalar(select(Livro).where((Livro.id == id)))
    if not db_livro:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=not_found_error(ENTITY))

    await session.delete(db_livro)

    await session.commit()

    return deleted_message(ENTITY)
