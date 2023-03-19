import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
import html
import hashlib

def savienot():
    conn = sqlite3.connect('planotajs.db', timeout=20)
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__,
            template_folder="templates",
            static_folder="static")
app.config["SECRET_KEY"] = "dsfn893ru9rubnfb"

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/par", methods=['GET', 'POST'])
def par():
    return render_template('par.html')

@app.route('/jauns_planotajs', methods=['GET', 'POST'])
def jauns_planotajs():
    conn = savienot()
    if request.method == "POST":
        prece = request.form.get('prece')
        cena = request.form.get('cena')
        kategorija = request.form.get('kategorija')
        conn.execute("INSERT INTO planotajs (prece, cena, kategorija) VALUES (?, ?, ?)", (prece, cena, kategorija))
        conn.commit()
        conn.close()
        return redirect(url_for('budzeta_planotajs', prece=prece, cena=cena, kategorija=kategorija))
    return render_template('jauns_planotajs.html')


@app.route("/budzeta_planotajs")
def budzeta_planotajs():
    conn = savienot()
    planotajs = conn.execute('SELECT prece, cena, kategorija FROM planotajs').fetchall()
    conn.close()
    return render_template('budzeta_planotajs.html', planotajs=planotajs)



@app.route("/registreties", methods=['GET', 'POST'])
def registreties():
    conn = savienot()
    if request.method == 'POST':
        lietotajvards = request.form['lietotajv']
        parole = request.form['parole']
        epasts = request.form['epasts']
        vards = request.form['vards']
        uzvards = request.form['uzvards']
        parole = hashlib.sha256(parole.encode('utf-8')).hexdigest()
        conn.execute("INSERT INTO lietotaji (lietotajvards, parole, epasts, vards, uzvards) VALUES (?, ?, ?, ?, ?)", (lietotajvards, parole, epasts, vards, uzvards))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template("registreties.html")

@app.route("/ienakt", methods=['GET', 'POST'])
def ienakt():
    conn = savienot()
    lietotaji = conn.execute('SELECT * FROM lietotaji').fetchall()
    conn.close()
    if request.method == 'POST':
        lietotajvards = request.form['lietotajv']
        parole = request.form['parole']
        parole = hashlib.sha256(parole.encode('utf-8')).hexdigest()
        for lietotajs in lietotaji:
            if lietotajvards == lietotajs['lietotajvards'] and parole == lietotajs['parole']:
                flash("Jūs esat ienācis!")
                return redirect(url_for('index'))
        flash("Nepareizs lietotājvārds vai parole!")
    return render_template('budzeta_planotajs.html')

@app.route("/<int:id>/labot", methods = ['GET', 'POST'])
def labot(id):
    conn = savienot()
    planotajs = conn.execute("SELECT id FROM planotajs WHERE id = ?", (id,)).fetchone()
    conn.close()
    if request.method == "POST":
        prece = request.form.get('prece')
        cena = request.form.get('cena')
        if not prece:
            flash("Ieraksti preci!")
            
        else: 
            conn = savienot()
            conn.execute("UPDATE planotajs SET prece=? , cena=? WHERE id=?", (prece, cena, id))
            conn.commit()
            conn.close()
            return redirect(url_for('budzeta_planotajs'))
            
    return render_template('labot.html', planotajs=planotajs)



if __name__ == '__main__':
    app.run(debug=True)
