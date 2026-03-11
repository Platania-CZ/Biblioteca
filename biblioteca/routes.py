from biblioteca import app
from flask import render_template
from biblioteca.models import Autore, ClassificazioneDewey, Editore, TipoOpera, Opera, Lettore, Prestito

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/opere')
def opere():
    items = Opera.query.all()
    return render_template('opere.html', items=items)

@app.route('/autori')
def autori():
    items = Autore.query.all()
    return render_template('autori.html', items=items)

@app.route('/lettori')
def lettori():
    items = Lettore.query.all()
    return render_template('lettori.html', items=items)

@app.route('/editori')
def editori():
    items = Editore.query.all()
    return render_template('editori.html', items=items)

@app.route('/prestiti')
def prestiti():
    items = Prestito.query.all()
    return render_template('prestiti.html', items=items)

@app.route('/tipi_opere')
def tipi_opere():
    items = TipoOpera.query.all()
    return render_template('tipi_opere.html', items=items)

@app.route('/dewey')
def dewey():
    items = ClassificazioneDewey.query.all()
    return render_template('dewey.html', items=items)

#Avvia l'applicazione
if __name__ == '__main__':
    app.run(debug=True)
    