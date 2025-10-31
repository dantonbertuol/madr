from http import HTTPStatus

from madr.routers.livros import ENTITY
from madr.schemas import LivroPublic
from madr.utils import conflict_error, deleted_message, not_found_error, sanitize_string


def test_create_livro(client, token, romancista):
    titulo = sanitize_string("A volta dos que não foram")
    response = client.post(
        "/livro",
        json={"titulo": titulo, "ano": 2024, "id_romancista": romancista.id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "ano": 2024,
        "titulo": titulo,
        "id_romancista": romancista.id,
        "id": 1,
    }


def test_create_livro_titulo_already_exist(client, romancista, token, livro):
    response = client.post(
        "/livro",
        json={"titulo": livro.titulo, "ano": 2024, "id_romancista": romancista.id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": conflict_error(ENTITY)}


def test_read_livros(client):
    response = client.get("/livro")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"livros": []}


def test_read_livros_with_livros(client, livro):
    livro_schema = LivroPublic.model_validate(livro).model_dump()
    response = client.get("/livro/")
    assert response.json() == {"livros": [livro_schema]}


def test_read_livro_with_titulo_ano_filter(client, livro):
    livro_schema = LivroPublic.model_validate(livro).model_dump()
    response = client.get(f"/livro/?titulo={livro.titulo}&ano={livro.ano}")
    assert response.json() == {"livros": [livro_schema]}


def test_read_livro(client, livro):
    response = client.get(f"/livro/{livro.id}")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "ano": livro.ano,
        "titulo": livro.titulo,
        "id_romancista": livro.id_romancista,
        "id": livro.id,
    }


def test_read_livro_not_found(client, livro):
    response = client.get("/livro/999")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": not_found_error(ENTITY)}


def test_update_livro(client, livro, token):
    titulo = sanitize_string("Catapimbas")
    response = client.patch(
        f"/livro/{livro.id}",
        json={"titulo": titulo},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "ano": livro.ano,
        "titulo": titulo,
        "id_romancista": livro.id_romancista,
        "id": livro.id,
    }


def test_update_livro_integrity_error(client, livro, other_livro, token):
    response_update = client.patch(
        f"/livro/{livro.id}",
        json={"titulo": other_livro.titulo},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {"detail": conflict_error(ENTITY)}


def test_update_livro_not_found(client, livro, token):
    response_update = client.patch(
        "/livro/9999",
        json={"titulo": livro.titulo},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response_update.status_code == HTTPStatus.NOT_FOUND
    assert response_update.json() == {"detail": not_found_error(ENTITY)}


def test_delete_livro(client, livro, token):
    response = client.delete(
        f"/livro/{livro.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == deleted_message(ENTITY)


def test_delete_livro_not_found(client, livro, token):
    response_update = client.delete("/livro/9999", headers={"Authorization": f"Bearer {token}"})

    assert response_update.status_code == HTTPStatus.NOT_FOUND
    assert response_update.json() == {"detail": not_found_error(ENTITY)}
