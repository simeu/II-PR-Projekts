import sqlite3


def savienot():
    conn = sqlite3.connect('planotajs.db')
    conn.row_factory = sqlite3.Row
    return conn

def slegt_savien(conn):
    conn.commit()
    conn.close()