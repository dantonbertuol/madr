from http import HTTPStatus

from madr.schemas import RomancistaPublic


def teste_create_romancista(client):
    response = client.post(
        "/romancistas",
        json={"nome": "danton"},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "nome": "danton",
        "id": 1,
    }


def test_create_romancista_nome_already_exist(client, romancista):
    response = client.post(
        "/romancistas",
        json={
            "nome": romancista.nome,
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": "Romancista already exists"}


def test_read_romancistas(client):
    response = client.get("/romancistas")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"romancistas": []}


def test_read_romancistas_with_romancistas(client, romancista):
    romancista_schema = RomancistaPublic.model_validate(romancista).model_dump()
    response = client.get("/romancistas/")
    assert response.json() == {"romancistas": [romancista_schema]}


def test_read_romancista(client, romancista):
    response = client.get(f"/romancistas/{romancista.id}")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "nome": romancista.nome,
        "id": romancista.id,
    }


def test_read_romancista_not_found(client, romancista):
    response = client.get("/romancistas/999")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Romancista not found"}


def test_update_romancista(client, romancista):
    response = client.patch(
        f"/romancistas/{romancista.id}",
        json={
            "nome": "bob",
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "nome": "bob",
        "id": romancista.id,
    }


def test_update_romancista_integrity_error(client, romancista, other_romancista):
    response_update = client.patch(
        f"/romancistas/{romancista.id}",
        json={
            "nome": other_romancista.nome,
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {"detail": "Romancista already exists"}


def test_update_romancista_not_found(client, romancista):
    response_update = client.patch(
        "/romancistas/9999",
        json={
            "nome": romancista.nome,
        },
    )

    assert response_update.status_code == HTTPStatus.NOT_FOUND
    assert response_update.json() == {"detail": "Romancista not found."}


def test_delete_romancista(client, romancista):
    response = client.delete(
        f"/romancistas/{romancista.id}",
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Romancista deleted"}


def test_delete_romancista_not_found(client, romancista):
    response_update = client.delete(
        "/romancistas/9999",
    )

    assert response_update.status_code == HTTPStatus.NOT_FOUND
    assert response_update.json() == {"detail": "Romancista not found."}
