"""Disposable browser-test server. Never use this entry point in production."""

import os
import tempfile
import uvicorn
from backend.app import create_app
from backend.db import connect
from backend.security import passwords
from backend.manage import DEMO

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as directory:
        app = create_app(
            os.path.join(directory, "browser.db"),
            "browser-test-only-secret-at-least-32-characters",
        )
        with connect(app.state.db_path) as db:
            db.execute(
                "INSERT INTO users(email,password_hash,role) VALUES (?,?,'admin')",
                ("admin@example.com", passwords.hash("AdminTesting42!")),
            )
            db.executemany(
                "INSERT INTO vehicles(make,model,category,price_cents,quantity) VALUES (?,?,?,?,?)",
                DEMO,
            )
        uvicorn.run(app, host="127.0.0.1", port=8000)
