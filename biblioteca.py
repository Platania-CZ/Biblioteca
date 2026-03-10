from flask import Flask, render_template
app = Flask(__name__, static_url_path='/static')   

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/opere')
def opere():
    items = [
        {'id': 1, 'titolo': 'Il Signore degli Anelli', 'autore': 'J.R.R. Tolkien', 'anno_pubblicazione': 1954},
        {'id': 2, 'titolo': '1984', 'autore': 'George Orwell', 'anno_pubblicazione': 1949},
        {'id': 3, 'titolo': 'Il Grande Gatsby', 'autore': 'F. Scott Fitzgerald', 'anno_pubblicazione': 1925}
    ]
    return render_template('opere.html', items=items)

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
    