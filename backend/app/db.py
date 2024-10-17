import sqlite3
from flask import g

DATABASE = 'database.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with open('schema.sql') as f:
        db.executescript(f.read())
    # Insert sample data
    insert_sample_data(db)

def insert_sample_data(db):
    db.execute("INSERT INTO user (username, password, totalCash) VALUES (?, ?, ?)", 
               ("testuser", generate_password_hash("testpass"), 10000))
    db.execute("INSERT INTO user (username, password, totalCash) VALUES (?, ?, ?)", 
               ("admin", generate_password_hash("adminpass"), 20000))
    db.commit()

def init_app(app):
    app.teardown_appcontext(close_db)
