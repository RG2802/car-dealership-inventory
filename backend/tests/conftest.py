import sqlite3
import pytest
from fastapi.testclient import TestClient
from backend.app import create_app
from .test_auth import SECRET

@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / 'test.db'), SECRET)
    with TestClient(app) as c:
        yield c

@pytest.fixture
def credentials():
    return {'email': 'buyer@example.com', 'password': 'CorrectHorse42!'}

@pytest.fixture
def user(client, credentials):
    response = client.post('/api/auth/register', json=credentials)
    assert response.status_code == 201
    return {'Authorization': 'Bearer ' + response.json()['access_token']}

@pytest.fixture
def admin(client, user):
    with sqlite3.connect(client.app.state.db_path) as db:
        db.execute("UPDATE users SET role='admin'")
    return user

