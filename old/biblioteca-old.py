import mysql.connector
from mysql.connector import cursor
from flask import Flask, render_template
app = Flask(__name__, static_url_path='/static')   

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="bibliodb"
)


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/opere')
def opere():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM opere")
    items = cursor.fetchall()

    return render_template('opere.html', items=items)

@app.route('/autori')
def autori():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM autori")
    items1 = cursor.fetchall()

    return render_template('autori.html', items=items1)

@app.route('/lettori')
def lettori():
    return render_template('home.html')

@app.route('/editori')
def editori():
    return render_template('home.html')

@app.route('/prestiti')
def prestiti():
    return render_template('home.html')

@app.route('/tipi_opere')
def tipi_opere():
    return render_template('tipi_opere.html')
#Avvia l'applicazione
if __name__ == '__main__':
    app.run(debug=True)
    