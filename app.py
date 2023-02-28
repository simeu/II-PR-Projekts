import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
import html


def savienot():
    conn = sqlite3.connect('planotajs.db')
    c = conn.cursor()
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
app.config["SECRET_KEY"] = "dsfn893ru9rubnfb"

@app.route('/')
def index():
    conn = savienot()
    prece = conn.execute('SELECT * FROM PartikasPreces').fetchall()
    conn.commit()
    conn.close()
    return render_template('index.html', prece=prece)

@app.route("/par")
def par():
    return render_template('par.html')


if __name__ == '__main__':
    app.run(debug=True)
