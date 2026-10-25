import sqlite3
import sys
import pytest
import jwt
from datetime import datetime, timedelta, timezone
from backend.app import create_app
from backend import manage
from .test_auth import SECRET


def test_secret_required(monkeypatch, tmp_path):
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError):
        create_app(str(tmp_path / "db"))


def test_deleted_user_token_rejected(client, user):
    with sqlite3.connect(client.app.state.db_path) as db:
        db.execute("DELETE FROM users")
    assert client.get("/api/vehicles", headers=user).status_code == 401


def test_expired_signed_token(client, user):
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {"sub": "1", "iat": now - timedelta(hours=2), "exp": now - timedelta(hours=1)},
        SECRET,
    )
    assert (
        client.get(
            "/api/vehicles", headers={"Authorization": "Bearer " + token}
        ).status_code
        == 401
    )


def test_seed_and_refuse_duplicate(client, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", client.app.state.db_path)
    monkeypatch.setattr(sys, "argv", ["manage", "seed"])
    manage.main()
    with sqlite3.connect(client.app.state.db_path) as db:
        assert db.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0] == 6
    with pytest.raises(SystemExit):
        manage.main()


def test_admin_creation_and_duplicate_refusal(client, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", client.app.state.db_path)
    monkeypatch.setattr(
        sys, "argv", ["manage", "create-admin", "--email", "operator@example.com"]
    )
    monkeypatch.setattr(manage.getpass, "getpass", lambda _: "OperatorTesting42!")
    manage.main()
    r = client.post(
        "/api/auth/login",
        json={"email": "operator@example.com", "password": "OperatorTesting42!"},
    )
    assert r.json()["user"]["role"] == "admin"
    with pytest.raises(sqlite3.IntegrityError):
        manage.main()
