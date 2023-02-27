import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
import html

def savienot():
    conn = sqlite3.connect('planotajs.db')
    c = conn.cursor()
    conn.row_factory = sqlite3.Row
    return conn

def paradit():
    conn = savienot()
    c = conn.cursor()
    radit = c.execute('SELECT * FROM planotajs').fetchall()
    conn.commit()
    conn.close()

    if radit is None:
        return "Netika atrasts neviens plānotājs. Pievienojiet to!"


app = Flask(__name__)
app.config["SECRET_KEY"] = "dsfn893ru9rubnfb"

@app.route('/')
def index():
    conn = savienot()
    c = conn.cursor()	
    planotajs = c.execute('SELECT * FROM planotajs').fetchall()
    conn.close()
    return render_template('welcomepage.html', planotajs=planotajs)

@app.route("/sakums", methods=('GET', 'POST'))
def sakums():
    return render_template("home.html")

@app.route("/budzeta_planotajs", methods=('GET', 'POST'))
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


@app.route('/jauns_planotajs', methods=('GET', 'POST'))
def jauns_planotajs():
    return render_template("jauns_planotajs.html")

if __name__ == '__main__':
    app.run(debug=True)



