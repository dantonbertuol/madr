from http import HTTPStatus

import pytest
from freezegun import freeze_time

from madr.utils import auth_error, permission_error


def test_create_user(client):
    response = client.post(
        "/conta",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "senha": "secret",
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "username": "alice",
        "email": "alice@example.com",
        "id": 1,
    }


def test_create_user_username_alredy_exists(client, user):
    response = client.post(
        "/conta",
        json={
            "username": user.username,
            "email": "alice@example.com",
            "senha": "secret",
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": "Username already exists"}


def test_create_user_email_alredy_exists(client, user):
    response = client.post(
        "/conta",
        json={
            "username": "alice",
            "email": user.email,
            "senha": "secret",
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": "Email already exists"}


def test_update_user(client, user, token):
    response = client.put(
        f"/conta/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "bob",
            "email": "bob@example.com",
            "senha": "mynewpassword",
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "bob",
        "email": "bob@example.com",
        "id": user.id,
    }


def test_update_integrity_error(client, user, other_user, token):
    response_update = client.put(
        f"/conta/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": other_user.username,
            "email": other_user.email,
            "senha": "mynewpassword",
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {"detail": "Username or Email already exists"}


def test_delete_user(client, user, token):
    response = client.delete(
        f"/conta/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}


def test_update_user_with_wrong_user(client, other_user, token):
    response = client.put(
        f"/conta/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "bob",
            "email": "bob@example.com",
            "senha": "mynewpassword",
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": permission_error()}


def test_delete_user_wrong_user(client, other_user, token):
    response = client.delete(
        f"/conta/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": permission_error()}


@pytest.mark.asyncio
async def test_get_token(client, user):
    response = client.post(
        "/conta/token",
        data={"username": user.email, "password": user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert "access_token" in token
    assert "token_type" in token


def test_token_expired_after_time(client, user):
    with freeze_time("2023-07-14 12:00:00"):
        response = client.post(
            "/conta/token",
            data={"username": user.email, "password": user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()["access_token"]

    with freeze_time("2023-07-14 13:01:00"):
        response = client.put(
            f"/conta/{user.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "wrongwrong",
                "email": "wrong@wrong.com",
                "senha": "wrong",
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials"}


def test_token_inexistent_user(client):
    response = client.post(
        "/conta/token",
        data={"username": "no_user@no_domain.com", "password": "testtest"},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": auth_error()}


def test_token_wrong_password(client, user):
    response = client.post("/conta/token", data={"username": user.email, "password": "wrong_password"})
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": auth_error()}


def test_refresh_token(client, token):
    response = client.post(
        "/conta/refresh_token",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


def test_token_expired_dont_refresh(client, user):
    with freeze_time("2023-07-14 12:00:00"):
        response = client.post(
            "/conta/token",
            data={"username": user.email, "password": user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()["access_token"]

    with freeze_time("2023-07-14 13:01:00"):
        response = client.post(
            "/conta/refresh_token",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials"}
