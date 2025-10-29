from http import HTTPStatus

from jwt import decode

from madr.security import create_access_token, settings


def test_jwt():
    data = {"test": "test"}
    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert decoded["test"] == data["test"]
    assert "exp" in decoded


def test_jwt_invalid_token(client):
    response = client.delete("/conta/1", headers={"Authorization": "Bearer token-invalido"})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_get_current_user_with_invalid_subject(client, user):
    data = {"test": "test"}
    token = create_access_token(data)
    response = client.delete(
        f"/conta/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}
    assert "WWW-Authenticate" in response.headers


def test_get_current_user_with_invalid_user(client, user):
    data = {"sub": "invalid_user"}
    token = create_access_token(data)
    response = client.delete(
        f"/conta/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}
    assert "WWW-Authenticate" in response.headers
