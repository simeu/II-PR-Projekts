import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
import hashlib
import re



def savienot(id=None):
    conn = sqlite3.connect('planotajs.db')
    conn.row_factory = sqlite3.Row
    if id:
        return conn.execute("SELECT * FROM planotajs WHERE id = ?", (id,))
    return conn


def sanemt(id):
    conn = savienot()
    ieraksts = conn.execute(
        "SELECT * FROM planotajs WHERE id = ?", (id,)).fetchone()
    conn.close()

    if ieraksts is None:
        ieraksts = {"prece": "Nezināms", "cena": "Nezināms"}

    return ieraksts

def validacija(cena_str):
    pattern = r'^\d{1,3}+\.\d{2}$'
    match = re.match(pattern, cena_str)
    if match:
        return True
    return False


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
        'SELECT *FROM planotajs').fetchall()
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
        if not prece:
            flash("Ievadiet preci!")
            return redirect(url_for('jauns_planotajs', prece=prece, cena=cena))
        elif not cena:
            flash("Ievadiet cenu!")
            return redirect(url_for('jauns_planotajs', prece=prece, cena=cena))
        elif validacija(cena) == True:
            conn.execute("INSERT INTO planotajs (id, prece, cena) VALUES (?, ?, ?)", (id, prece, cena))
            conn.commit()
            conn.close()
            return redirect(url_for('budzeta_planotajs', prece=prece, cena=cena)) 
        else:
            flash("Cenai ir jābūt skaitliskai vērtībai! Mēģiniet vēlreiz.")
    return render_template('jauns_planotajs.html')


@app.route("/<int:id>/labot", methods=['GET', 'POST'])  # Ierakstu labošana.
def labot(id):
    planotajs = sanemt(id)
    if request.method == "POST":
        id = request.form.get('id')
        prece = request.form.get('prece')
        cena = request.form.get('cena')

        if not prece:
            flash("Ieraksti preci!")

        elif not cena:
            flash("Ieraksti cenu!")

        elif validacija(cena) == True:
            conn = savienot()
            conn.execute(
                "UPDATE planotajs SET prece=?, cena=? WHERE id=?", (prece, cena, id))
            conn.commit()
            conn.close()
            flash("Ieraksts veiksmīgi labots!")
            return render_template("budzeta_planotajs.html", planotajs=planotajs, prece=prece, cena=cena, id=id)

        else:
            flash("Notikusi kļūda! Mēģiniet vēlreiz.")
    return render_template('labot.html', planotajs=planotajs)


@app.route("/<int:id>/dzest", methods=('POST',))  # Ierakstu dzēšana.
def dzest(id):
    planotajs = sanemt(id)
    conn = savienot()
    conn.execute("DELETE FROM planotajs WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Ieraksts veiksmīgi dzēsts!")
    return render_template('budzeta_planotajs.html', planotajs=planotajs)


# Tiek reģistrēts jauns lietotājs.
@app.route("/registreties", methods=['GET', 'POST'])
def registreties():
    if request.method == "POST":
        lietotajv = request.form.get('lietotajvards')
        parole = request.form.get('parole')
        hash_parole = hashlib.md5(parole.encode()).hexdigest()
        if len(parole) < 5 or len(parole) > 10:
            flash("Parolei jābūt no 5 līdz 10 rakstzīmēm!")
        elif len(lietotajv) < 5 or len(lietotajv) > 10:
            flash("Lietotājvārdam jābūt no 5 līdz 10 rakstzīmēm!")
        conn = savienot()
        conn.execute(
            "INSERT INTO lietotajs (lietotajvards, parole) VALUES (?, ?)", (lietotajv, hash_parole))
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
        lietotajs = lietotajs["lietotajvards"]
        conn.close()
        if lietotajs is None:
            flash(
                "Lietotājs nav atrasts! Lūdzu reģistrējieties vai pārbaudiet rakstzīmes!")
        elif parole is None:
            flash("Ievadiet, lūdzu, paroli!")
        else: 
            conn = savienot()
            parole2 = conn.execute("SELECT parole FROM lietotajs WHERE lietotajvards = ?", (lietotajvards,)).fetchone()
            conn.close()
            hash_parole = hashlib.md5(parole.encode()).hexdigest()
            if lietotajs != lietotajvards:
                flash("Lietotājs nav atrasts! Lūdzu reģistrējieties vai pārbaudiet rakstzīmes!")
            elif parole2["parole"] != hash_parole:
                flash("Parole nav pareiza! Mēģiniet vēlreiz!")
            else:
                return redirect(url_for('budzeta_planotajs'))
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
