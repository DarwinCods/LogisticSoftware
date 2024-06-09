import sqlite3
from flask import g

DATABASE = 'inventory.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one = False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def init_db():
    with open('schema.sql', mode='r') as f:
        get_db().cursor().executescript(f.read())
    get_db().commit()

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
