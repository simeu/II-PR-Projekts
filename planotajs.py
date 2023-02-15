import sqlite3
from flask import Flask, render_template
import html

with open("projekts.html") as f:
    projekts = f.read()
    

def savienot():
    conn = sqlite3.connect('planotajs.db')
    c = conn.cursor()
    conn.row_factory = sqlite3.Row
    return conn



app = Flask(__name__)

@app.route('/')
def index():
    return render_template(projekts)

@app.route("/sakums")
def sakums():
    return render_template("sakums.html")

@app.route("/planotajs")
def planotajs():
    return "/"



if __name__ == '__main__':
    app.run(debug=True)



