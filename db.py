import os
import sqlite3
from flask import g, current_app


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


def connect_db(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(app):
    db_path = app.config.get('DATABASE')
    if not db_path:
        raise RuntimeError('DATABASE path not set in app.config')
    # Ensure directory exists
    dirname = os.path.dirname(db_path)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_name TEXT NOT NULL,
        client_name TEXT,
        address TEXT,
        status TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_name TEXT NOT NULL,
        category TEXT,
        mobile TEXT,
        daily_wage REAL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        site_id INTEGER NOT NULL,
        worker_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        overtime_hours REAL,
        FOREIGN KEY(site_id) REFERENCES sites(id),
        FOREIGN KEY(worker_id) REFERENCES workers(id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        site_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        remarks TEXT,
        FOREIGN KEY(site_id) REFERENCES sites(id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS material_register (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        site_id INTEGER NOT NULL,
        material TEXT NOT NULL,
        unit TEXT,
        quantity_received REAL,
        quantity_used REAL,
        balance REAL,
        FOREIGN KEY(site_id) REFERENCES sites(id)
    )
    """)
    conn.commit()
    conn.close()


def close_db(e=None):
    from flask import g
    db = g.pop('db', None)
    if db is not None:
        db.close()
