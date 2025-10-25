from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


@table_registry.mapped_as_dataclass
class Romancista:
    __tablename__ = "romancistas"
    # https://docs.sqlalchemy.org/en/20/orm/mapping_api.html#sqlalchemy.orm.mapped_column
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    nome: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now(), onupdate=func.now())

    livros: Mapped[list["Livro"]] = relationship(
        init=False, cascade="all, delete-orphan", lazy="selectin", back_populates="romancista"
    )


@table_registry.mapped_as_dataclass
class Livro:
    __tablename__ = "livros"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    ano: Mapped[int]
    titulo: Mapped[str] = mapped_column(unique=True)
    id_romancista: Mapped[int] = mapped_column(ForeignKey("romancistas.id"))

    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now(), onupdate=func.now())

    romancista: Mapped["Romancista"] = relationship(init=False, lazy="joined", back_populates="livros")


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    senha: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now(), onupdate=func.now())
