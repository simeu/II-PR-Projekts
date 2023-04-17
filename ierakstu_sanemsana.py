import db_savienotajs as db

def sanemt(id):
    conn = db()
    ieraksts = conn.execute("SELECT * FROM planotajs WHERE id = ?", (id,)).fetchone()
    conn.close()
    
    if ieraksts is None:
        ieraksts = {"prece": "Nezināms", "cena": "Nezināms"}

    return ieraksts

