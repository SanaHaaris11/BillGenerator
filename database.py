import sqlite3
from flask import g
import os

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with open('schema.sql', 'r') as f:
        schema = f.read()
    db = get_db()
    db.executescript(schema)
    db.commit()

def init_app(app):
    app.teardown_appcontext(close_connection)
    with app.app_context():
        init_db()