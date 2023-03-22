import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
import html
import hashlib

def savienot():
    conn = sqlite3.connect('planotajs.db', timeout=20) #Tiek veiktw savienojums ar datubāzi, specializēti HTML.
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__,
            template_folder="templates",
            static_folder="static")
app.config["SECRET_KEY"] = "dsfn893ru9rubnfb" #Tiek noteiktas mapes, kuras tiek izmantotas (piem. templates - HTML failiem) un drošības atslēga.

@app.route('/') #Tiek nostādīta Index lapa, uz kuras balstīsies pārējie HTML faili.
def index():
    return render_template('index.html')

@app.route("/par", methods=['GET', 'POST'])
def par():
    return render_template('par.html')

@app.route('/jauns_planotajs', methods=['GET', 'POST']) #Tiek izveidots jauns ieraksts.
def jauns_planotajs():
    conn = savienot()
    if request.method == "POST":
        id = request.form.get('id')
        prece = request.form.get('prece')
        cena = request.form.get('cena')
        conn.execute("INSERT INTO planotajs (id, prece, cena) VALUES (?, ?, ?)", (id, prece, cena))
        conn.commit()
        conn.close()
        return redirect(url_for('budzeta_planotajs', prece=prece, cena=cena))
    return render_template('jauns_planotajs.html')


@app.route("/budzeta_planotajs") #Tiek parādīts plānotājs (visi ieraksti no datubāzes), kā arī "cena" tiek sasummēta, lai redzētu kopējos tēriņus. 
def budzeta_planotajs():
    conn = savienot()
    planotajs = conn.execute('SELECT id, prece, cena FROM planotajs').fetchall()
    summa = conn.execute("SELECT SUM(cena) FROM planotajs").fetchone()[0]
    conn.close()
    return render_template('budzeta_planotajs.html', planotajs=planotajs, summa=summa)



@app.route("/registreties", methods=['GET', 'POST']) #Reģistrācija.
def registreties():
    conn = savienot()
    if request.method == 'POST':
        lietotajvards = request.form['lietotajv']
        parole1 = request.form['parole']
        epasts = request.form['epasts']
        vards = request.form['vards']
        uzvards = request.form['uzvards']
        parole2 = hashlib.sha256(parole1.encode('utf-8')).hexdigest()
        conn.execute("INSERT INTO lietotaji (lietotajvards, parole, epasts, vards, uzvards) VALUES (?, ?, ?, ?, ?)", (lietotajvards, parole2, epasts, vards, uzvards))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template("registreties.html")

@app.route("/ienakt", methods=['GET', 'POST']) #Pieslēgšanās.
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
    return render_template('ienakt.html')

@app.route("/<int:id>/labot", methods = ['GET', 'POST']) #Ieraksta labošana.
def labot(id):
    conn = savienot()
    planotajs = conn.execute("SELECT id FROM planotajs WHERE id = ?", (id,)).fetchone()[0]
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
            flash("Ieraksts veiksmīgi labots!")
            return redirect(url_for('budzeta_planotajs'))
            
    return render_template('labot.html', planotajs=planotajs)

@app.route("/<int:id>/dzest", methods = ['POST']) #Ieraksta dzēšana. 
def dzest(id):
    conn = savienot()
    conn.execute("SELECT * FROM planotajs WHERE id = ?", (id,)).fetchone()[0]
    conn.execute("DELETE FROM planotajs WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Ieraksts dzēsts.")
    return redirect(url_for('index'))
     
if __name__ == '__main__':
    app.run(debug=True)
