import sqlite3
import os
import click
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db_path = current_app.config['DATABASE']  # Use the configured database path
    
    # Remove existing database file
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create new database and tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables from schema.sql
    with open('schema.sql', 'r') as f:
        cursor.executescript(f.read())
    
    conn.commit()
    conn.close()

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)  # This line registers the command

