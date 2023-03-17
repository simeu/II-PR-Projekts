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
    return render_template('index.html')

@app.route("/par", methods=['GET', 'POST'])
def par():
    return render_template('par.html')

@app.route('/jauns_planotajs', methods=['GET', 'POST'])
def jauns_planotajs():
    conn = savienot()
    if request.method == "POST":
        try:
            prece = request.form['prece']
        except KeyError:
            flash("Lūdzu, ievadiet preci!")
            return redirect(url_for("jauns_planotajs"))       
        cena = request.form['cena']
        kategorija = request.form['kategorija']
        ievietot = conn.execute("INSERT INTO planotajs (prece, cena, kategorija) VALUES (?, ?, ?)", (prece, cena, kategorija))
        conn.commit()
        conn.close()
        flash("Ieraksts veiksmīgi pievienots!")
        return redirect(url_for("budzeta_planotajs"))
    return render_template('jauns_planotajs.html')


@app.route("/budzeta_planotajs")
def budzeta_planotajs():
    conn = savienot()
    if request.method == "GET":
        planotajs = conn.execute('SELECT * FROM planotajs').fetchall()
        cena = conn.execute('SELECT cena FROM planotajs').fetchall()
        prece = conn.execute('SELECT prece FROM planotajs').fetchall()
        return render_template('budzeta_planotajs.html', planotajs=planotajs, cena=cena, prece=prece)
    return redirect(url_for('index'))


@app.route("/ienakt", methods=['GET', 'POST'])
def ienakt():
    conn = savienot()
    lietotaji = conn.execute('SELECT * FROM lietotaji').fetchall()
    if request.method == 'POST':
        lietotajvards = request.form['lietotajv']
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
        

@app.route("/registreties", methods=['GET', 'POST'])
def registreties():
    conn = savienot()
    c = conn.cursor()
    if request.method == 'POST':
        lietotajvards = request.form['lietotajv']
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
