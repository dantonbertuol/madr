from http import HTTPStatus

from madr.schemas import RomancistaPublic
from madr.utils import conflict_error, not_found_error, sanitize_string

ENTITY: str = "Romancista"


def teste_create_romancista(client):
    name = sanitize_string("danton")
    response = client.post(
        "/romancista",
        json={"nome": name},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "nome": name,
        "id": 1,
    }


def test_create_romancista_nome_already_exist(client, romancista):
    response = client.post(
        "/romancista",
        json={
            "nome": romancista.nome,
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": conflict_error(ENTITY)}


def test_read_romancistas(client):
    response = client.get("/romancista")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"romancistas": []}


def test_read_romancistas_with_romancistas(client, romancista):
    romancista_schema = RomancistaPublic.model_validate(romancista).model_dump()
    response = client.get("/romancista/")
    assert response.json() == {"romancistas": [romancista_schema]}


def test_read_romancistas_with_name_filter(client, romancista):
    romancista_schema = RomancistaPublic.model_validate(romancista).model_dump()
    response = client.get(f"/romancista/?nome={romancista.nome}")
    assert response.json() == {"romancistas": [romancista_schema]}


def test_read_romancista(client, romancista):
    response = client.get(f"/romancista/{romancista.id}")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "nome": romancista.nome,
        "id": romancista.id,
    }


def test_read_romancista_not_found(client, romancista):
    response = client.get("/romancista/999")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": not_found_error(ENTITY)}


def test_update_romancista(client, romancista):
    name = sanitize_string("bob")
    response = client.patch(
        f"/romancista/{romancista.id}",
        json={
            "nome": name,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "nome": name,
        "id": romancista.id,
    }


def test_update_romancista_integrity_error(client, romancista, other_romancista):
    response_update = client.patch(
        f"/romancista/{romancista.id}",
        json={
            "nome": other_romancista.nome,
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {"detail": conflict_error(ENTITY)}


def test_update_romancista_not_found(client, romancista):
    response_update = client.patch(
        "/romancista/9999",
        json={
            "nome": romancista.nome,
        },
    )

    assert response_update.status_code == HTTPStatus.NOT_FOUND
    assert response_update.json() == {"detail": not_found_error(ENTITY)}


def test_delete_romancista(client, romancista):
    response = client.delete(
        f"/romancista/{romancista.id}",
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Romancista deleted"}


def test_delete_romancista_not_found(client, romancista):
    response_update = client.delete(
        "/romancista/9999",
    )

    assert response_update.status_code == HTTPStatus.NOT_FOUND
    assert response_update.json() == {"detail": not_found_error(ENTITY)}
