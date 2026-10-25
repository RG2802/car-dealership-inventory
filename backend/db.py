"""SQLite connections are short-lived; database constraints protect invariants."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

@contextmanager
def connect(path):
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    try:
        with db:
            yield db
    finally:
        db.close()

def initialize(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user','admin'))
            );
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                make TEXT NOT NULL, model TEXT NOT NULL, category TEXT NOT NULL,
                price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
                quantity INTEGER NOT NULL CHECK(quantity BETWEEN 0 AND 1000000)
            );
        ''')
