import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
import hashlib


def savienot(id=None):
    conn = sqlite3.connect('planotajs.db')
    conn.row_factory = sqlite3.Row
    if id:
        conn.execute("SELECT * FROM planotajs WHERE id = ?", (id,))
    return conn


def sanemt(id):
    conn = savienot()
    ieraksts = conn.execute(
        "SELECT * FROM planotajs WHERE id = ?", (id,)).fetchone()
    conn.close()

    if ieraksts is None:
        ieraksts = {"prece": "Nezināms", "cena": "Nezināms"}

    return ieraksts


app = Flask(__name__,
            template_folder="templates",
            static_folder="static")
app.config["SECRET_KEY"] = "dsfn893ru9rubnfb"


@app.route('/')
def index():
    return render_template('par.html')


@app.route("/budzeta_planotajs")
def budzeta_planotajs():
    conn = savienot()
    planotajs = conn.execute(
        'SELECT id, prece, cena FROM planotajs').fetchall()
    summa = conn.execute("SELECT SUM(cena) FROM planotajs").fetchone()[0]
    conn.close()
    return render_template('budzeta_planotajs.html', planotajs=planotajs, summa=summa)


# Tiek izveidots jauns ieraksts.
@app.route('/jauns_planotajs', methods=['GET', 'POST'])
def jauns_planotajs():
    conn = savienot()
    if request.method == "POST":
        id = request.form.get('id')
        prece = request.form.get('prece')
        cena = request.form.get('cena')
        conn.execute(
            "INSERT INTO planotajs (id, prece, cena) VALUES (?, ?, ?)", (id, prece, cena))
        conn.commit()
        conn.close()
        return redirect(url_for('budzeta_planotajs', prece=prece, cena=cena))
    return render_template('jauns_planotajs.html')


@app.route("/<int:id>/labot", methods=['GET', 'POST'])  # Ierakstu labošana.
def labot(id):
    planotajs = sanemt(id)
    if request.method == "POST":
        prece = request.form.get('prece')
        cena = request.form.get('cena')
        if not prece:
            flash("Ieraksti preci!")

        elif not cena:
            flash("Ieraksti cenu!")

        elif cena != int or float:
            flash("Cenai ir jābūt skaitlim!")

        else:
            conn = savienot()
            conn.execute(
                "UPDATE planotajs SET prece=?, cena=? WHERE id=?", (prece, cena))
            conn.commit()
            conn.close()
            flash("Ieraksts veiksmīgi labots!")
            return redirect(url_for('budzeta_planotajs'))

    return render_template('labot.html', planotajs=planotajs)


@app.route("/<int:id>/dzest", methods=('POST',))  # Ierakstu dzēšana.
def dzest(id):
    planotajs = sanemt(id)
    conn = savienot()
    conn.execute("DELETE FROM planotajs WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Ieraksts veiksmīgi dzēsts!")
    return redirect(url_for('budzeta_planotajs'), planotajs=planotajs)


# Tiek reģistrēts jauns lietotājs.
@app.route("/registreties", methods=['GET', 'POST'])
def registreties():
    if request.method == "POST":
        lietotajvards = request.form.get('lietotajvards')
        parole = request.form.get('parole')
        hash_parole = hashlib.md5(parole.encode())
        conn = savienot()
        conn.execute("INSERT INTO lietotajs (lietotajvards, parole) VALUES (?, ?)",
                     (lietotajvards, hash_parole))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('registreties.html')


@app.route("/ienakt", methods=['GET', 'POST'])
def ienakt():
    if request.method == "POST":
        lietotajvards = request.form.get('lietotajvards')
        parole = request.form.get('parole')
        conn = savienot()
        lietotajs = conn.execute(
            "SELECT * FROM lietotajs WHERE lietotajvards = ?", (lietotajvards,)).fetchone()
        conn.close()
        hash_parole = hashlib.md5(parole.encode())
        # Pievienot pareizu paroļu atpazīšanas algoritmu (salīdzina ar encrypted paroli, nevis lietotāja ievadīto).
        if lietotajs is None:
            flash(
                "Lietotājs nav atrasts! Lūdzu reģistrējieties vai pārbaudiet rakstzīmes!")
        elif lietotajs != parole:
            flash("Nepareiza parole! Mēģiniet vēlreiz!")
        elif parole != hash_parole:
            flash("Nepareiza parole! Mēģiniet vēlreiz!")
        else:
            return redirect(url_for('budzeta_planotajs'))
    return render_template('login.html')


# Tiek parādīts lietotāja profils.
@app.route("/profils/<int:id>", methods=['GET', 'POST'])
def profils(id):
    conn = savienot()
    lietotajs = conn.execute(
        "SELECT * FROM lietotajs WHERE id = ?", (id,)).fetchone()
    # Global Variables

    conn.close()
    return render_template('profils.html', lietotajs=lietotajs)


if __name__ == '__main__':
    app.run(debug=True)
