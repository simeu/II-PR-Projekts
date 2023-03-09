import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
import html
import hashlib


def savienot():
    conn = sqlite3.connect('planotajs.db')
    c = conn.cursor()
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__,
            template_folder="templates",
            static_folder="static")
app.config["SECRET_KEY"] = "dsfn893ru9rubnfb"

@app.route('/')
def index():
    conn = savienot()
    prece = conn.execute('SELECT * FROM  veids').fetchall()
    conn.commit()
    conn.close()
    return render_template('index.html', prece=prece)

@app.route("/par", methods=['GET', 'POST'])
def par():
    return render_template('par.html')

@app.route("/budzeta_planotajs")
def budzeta_planotajs():
    conn = savienot()
    c = conn.cursor()
    if request.method == 'POST':
        ievade = request.form['ievade']
        ievade = html.escape(ievade)
        c.execute("INSERT INTO planotajs (ievade) VALUES (?)", (ievade,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('budzeta_planotajs.html')

@app.route("/ienakt", methods=['GET', 'POST'])
def ienakt():
    conn = savienot()
    lietotaji = conn.execute('SELECT * FROM lietotaji').fetchall()
    if request.method == 'POST':
        lietotajvards = request.form['lietotajvards']
        parole = request.form['parole']
        parole = hashlib.sha256(parole.encode('utf-8')).hexdigest()
        for lietotajs in lietotaji:
            if lietotajvards == lietotajs['lietotajvards'] and parole == lietotajs['parole']:
                flash("Jūs esat ienācis!")
                return redirect(url_for('index'))
            else:
                flash("Nepareizs lietotājvārds vai parole!")
                return redirect(url_for('ienakt'))
    return render_template('login.html')

@app.route('/jauns_planotajs', methods=['GET', 'POST'])
def jauns_planotajs():
    return render_template("jauns_planotajs.html")

@app.route("/registreties", methods=['GET', 'POST'])
def registreties():
    conn = savienot()
    c = conn.cursor()
    if request.method == 'POST':
        lietotajvards = request.form['lietotajvards']
        parole = request.form['parole']
        epasts = request.form['epasts']
        vards = request.form['vards']
        uzvards = request.form['uzvards']
        parole = hashlib.sha256(parole.encode('utf-8')).hexdigest()
        c.execute("INSERT INTO lietotaji (lietotajvards, parole, epasts, vards, uzvards) VALUES (?, ?, ?, ?, ?)", (lietotajvards, parole, epasts, vards, uzvards))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template("registreties.html")


if __name__ == '__main__':
    app.run(debug=True)
