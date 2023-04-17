import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
import hashlib
import db_savienotajs as db
import ierakstu_sanemsana as ieraksti


app = Flask(__name__,
            template_folder="templates",
            static_folder="static")
app.config["SECRET_KEY"] = "dsfn893ru9rubnfb" #Tiek noteiktas mapes, kuras tiek izmantotas (piem. templates - HTML failiem) un drošības atslēga.



@app.route('/') #Tiek nostādīta Index lapa, uz kuras balstīsies pārējie HTML faili.
def index():
    return render_template('par.html')
'''
@app.route("/par", methods=['GET', 'POST'])
def par():
    return render_template('par.html')
'''
@app.route("/budzeta_planotajs") #Tiek parādīts plānotājs (visi ieraksti no datubāzes), kā arī "cena" tiek sasummēta, lai redzētu kopējos tēriņus. 
def budzeta_planotajs():
    conn = db()
    planotajs = conn.execute('SELECT id, prece, cena FROM planotajs').fetchall()
    summa = conn.execute("SELECT SUM(cena) FROM planotajs").fetchone()[0]
    conn.close()
    return render_template('budzeta_planotajs.html', planotajs=planotajs, summa=summa)

@app.route('/jauns_planotajs', methods=['GET', 'POST']) #Tiek izveidots jauns ieraksts.
def jauns_planotajs():
    conn = db()
    if request.method == "POST":
        id = request.form.get('id')
        prece = request.form.get('prece')
        cena = request.form.get('cena')
        conn.execute("INSERT INTO planotajs (id, prece, cena) VALUES (?, ?, ?)", (id, prece, cena))
        conn.commit()
        conn.close()
        return redirect(url_for('budzeta_planotajs', prece=prece, cena=cena))
    return render_template('jauns_planotajs.html')


@app.route("/<int:id>/labot", methods = ['GET', 'POST']) #Ierakstu labošana.
def labot(id):
    planotajs = db(id)
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
            conn = db()
            conn.execute("UPDATE planotajs SET prece=?, cena=? WHERE id=?", (prece, cena, id))
            conn.commit()
            conn.close()
            flash("Ieraksts veiksmīgi labots!")
            return redirect(url_for('budzeta_planotajs'))
            
    return render_template('labot.html', planotajs=planotajs)

@app.route("/<int:id>/dzest", methods = ('POST',))#Ierakstu dzēšana.
def dzest(id):
    planotajs = db(id)
    conn = db()
    conn.execute("DELETE FROM planotajs WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Ieraksts veiksmīgi dzēsts!")
    return redirect(url_for('budzeta_planotajs'))

@app.route("/registreties", methods=['GET', 'POST']) #Tiek reģistrēts jauns lietotājs.
def registreties():
    if request.method == "POST":
        lietotajvards = request.form.get('lietotajvards')
        parole = request.form.get('parole')
        parole2 = parole.sha256.encode('utf-8').hexdigest()
        conn = db()
        conn.execute("INSERT INTO lietotaji (lietotajvards, parole) VALUES (?, ?)", (lietotajvards, parole2))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('registreties.html')

@app.route("/ienakt", methods=['GET', 'POST']) #Lietotājs pieslēdzas sistēmai.
def ienakt():
    if request.method == "POST":
        lietotajvards = request.form.get('lietotajvards')
        parole = request.form.get('parole')
        conn = db()
        lietotajs = conn.execute("SELECT * FROM lietotaji WHERE lietotajvards = ?", (lietotajvards,)).fetchone()
        conn.close()
        if lietotajs is None: #Pievienot pareizu paroļu atpazīšanas algoritmu (salīdzina ar encrypted paroli, nevis lietotāja ievadīto).
            flash("Lietotājs nav atrasts! Lūdzu reģistrējieties vai pārbaudiet rakstzīmes!")
        elif lietotajs[id] != parole:
            flash("Nepareiza parole! Mēģiniet vēlreiz!")
        else:
            return redirect(url_for('budzeta_planotajs'))
    return render_template('login.html')

@app.route("/profils/<int:id>", methods=['GET', 'POST']) #Tiek parādīts lietotāja profils.
def profils(id):
    conn = db()
    lietotajs = conn.execute("SELECT * FROM lietotaji WHERE id = ?", (id,)).fetchone()
    # Global Variables
    
    conn.close()
    return render_template('profils.html', lietotajs=lietotajs)
    
if __name__ == '__main__':
    app.run(debug=True)
