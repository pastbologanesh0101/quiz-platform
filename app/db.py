"""Low-level SQLite schema and connection helpers."""
from flask import current_app

SCHEMA = """
CREATE TABLE IF NOT EXISTS quiz (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS question (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    choice_a TEXT NOT NULL,
    choice_b TEXT NOT NULL,
    choice_c TEXT NOT NULL,
    choice_d TEXT NOT NULL,
    correct_index INTEGER NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quiz (id)
);

CREATE TABLE IF NOT EXISTS attempt (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    total INTEGER NOT NULL,
    taken_at TEXT NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quiz (id)
);
"""


def init_db(conn):
    conn.executescript(SCHEMA)
    conn.commit()


def get_db():
    """Return the shared SQLite connection for the current app."""
    return current_app.config["DB_CONN"]
