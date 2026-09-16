"""Online Quiz Platform - Flask application factory."""
import os
import sqlite3

from flask import Flask


def create_app(testing=False, db_path=None):
    """Application factory.

    Args:
        testing: When True, uses an in-memory SQLite database and enables
            Flask's TESTING mode (so error handlers raise instead of
            rendering error pages, and no on-disk state is created).
        db_path: Optional explicit path to the SQLite database file. Mostly
            useful for tests that want a fresh temp file instead of the
            default in-memory database.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config["TESTING"] = testing
    app.config["SECRET_KEY"] = "dev"  # fine for this small demo project

    if db_path is None:
        if testing:
            db_path = ":memory:"
        else:
            os.makedirs(app.instance_path, exist_ok=True)
            db_path = os.path.join(app.instance_path, "quiz.db")

    # A single, shared connection is kept for the lifetime of the app. This
    # is what lets an in-memory SQLite database survive across requests
    # (each new connection to ":memory:" would otherwise be a fresh, empty
    # database).
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    app.config["DB_CONN"] = conn

    from . import db as db_module

    db_module.init_db(conn)

    from . import seed

    seed.seed_if_empty(conn)

    from . import routes

    app.register_blueprint(routes.bp)

    return app
