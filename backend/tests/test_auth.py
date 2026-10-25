import sqlite3
import jwt
from datetime import datetime, timedelta, timezone
import pytest

SECRET = "test-only-secret-at-least-32-characters-long"


def test_register_login_and_password_hash(client, credentials):
    response = client.post("/api/auth/register", json=credentials)
    assert response.status_code == 201
    assert response.json()["user"] == {
        "id": 1,
        "email": credentials["email"],
        "role": "user",
    }
    assert client.post("/api/auth/login", json=credentials).status_code == 200
    with sqlite3.connect(client.app.state.db_path) as db:
        stored = db.execute("SELECT password_hash FROM users").fetchone()[0]
    assert stored != credentials["password"]
    assert stored.startswith("$argon2")


def test_duplicate_email_case_insensitive(client, credentials):
    client.post("/api/auth/register", json=credentials)
    credentials["email"] = "BUYER@example.com"
    assert client.post("/api/auth/register", json=credentials).status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "invalid", "password": "CorrectHorse42!"},
        {"email": "ok@example.com", "password": "short"},
        {"email": "ok@example.com", "password": "CorrectHorse42!", "role": "admin"},
    ],
)
def test_invalid_registration(client, payload):
    assert client.post("/api/auth/register", json=payload).status_code == 422


def test_wrong_credentials(client, user, credentials):
    credentials["password"] = "wrong-password"
    assert client.post("/api/auth/login", json=credentials).status_code == 401
    credentials["email"] = "missing@example.com"
    assert client.post("/api/auth/login", json=credentials).status_code == 401


@pytest.mark.parametrize(
    "token",
    [
        "",
        "garbage",
        jwt.encode(
            {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
            SECRET,
        ),
    ],
)
def test_missing_invalid_expired_tokens(client, token):
    assert (
        client.get(
            "/api/vehicles", headers={"Authorization": "Bearer " + token}
        ).status_code
        == 401
    )


def test_me(client, user):
    assert client.get("/api/auth/me", headers=user).json()["role"] == "user"
