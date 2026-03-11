from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/bibliotecadb'
db = SQLAlchemy(app)

#definizione del modello
class Autore(db.Model):
    __tablename__ = 'autori'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100), nullable=False)
    nazionalita = db.Column(db.String(100), nullable=False)
    data_nascita = db.Column(db.Date, nullable=True)

    # Relazione con le opere scritte
    opere = db.relationship('Opera', backref='autore', lazy=True)

    def __repr__(self):
        return f'<Autore {self.nome} {self.cognome}>'

class ClassificazioneDewey(db.Model):
    __tablename__ = 'classificazione_dewey'
    
    id = db.Column(db.Integer, primary_key=True)
    descrizione = db.Column(db.String(255), nullable=False)
    sezione_principale = db.Column(db.String(3), nullable=False)
    sottosezione = db.Column(db.String(20), nullable=True)

    # Relazione con le opere classificate
    opere = db.relationship('Opera', backref='classificazione', lazy=True)

    @property
    def codice_dewey(self):
        if self.sottosezione:
            return f"{self.sezione_principale}.{self.sottosezione}"
        return self.sezione_principale

    def __repr__(self):
        return f'<ClassificazioneDewey {self.codice_dewey} - {self.descrizione}>'

class Editore(db.Model):
    __tablename__ = 'editori'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    sede = db.Column(db.String(100), nullable=True)

    # Relazione con le copie prodotte
    copie = db.relationship('Copia', backref='editore', lazy=True)

    def __repr__(self):
        return f'<Editore {self.nome}>'

class TipoOpera(db.Model):
    __tablename__ = 'tipi_opere'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False) # Es: Romanzo, Saggio, Rivista

    opere = db.relationship('Opera', backref='tipo', lazy=True)

    def __repr__(self):
        return f'<TipoOpera {self.nome}>'

class Opera(db.Model):
    __tablename__ = 'opere'

    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(255), nullable=False)
    
    # Chiavi Esterne
    id_autore = db.Column(db.Integer, db.ForeignKey('autori.id'), nullable=False)
    id_tipo_opera = db.Column(db.Integer, db.ForeignKey('tipi_opere.id'), nullable=False)
    id_dewey = db.Column(db.Integer, db.ForeignKey('classificazione_dewey.id'), nullable=True)
    
    isbn_generale = db.Column(db.String(20), nullable=True)
    note = db.Column(db.Text, nullable=True)

    # Relazione con le copie fisiche
    copie = db.relationship('Copia', backref='opera', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Opera "{self.titolo}">'

class Copia(db.Model):
    __tablename__ = 'copie'

    id = db.Column(db.Integer, primary_key=True)
    id_opera = db.Column(db.Integer, db.ForeignKey('opere.id'), nullable=False)
    id_editore = db.Column(db.Integer, db.ForeignKey('editori.id'), nullable=False)
    
    isbn = db.Column(db.String(20), nullable=True)
    anno_pubblicazione = db.Column(db.Integer, nullable=True)
    posizione_scaffale = db.Column(db.String(50), nullable=True)
    stato = db.Column(db.String(100), default="Disponibile")

    # Relazione con i prestiti subiti da questa specifica copia
    prestiti = db.relationship('Prestito', backref='copia', lazy=True)

    def __repr__(self):
        return f'<Copia ID {self.id} di "{self.opera.titolo}"> '

class Lettore(db.Model):
    __tablename__ = 'lettori'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100), nullable=False)
    codice_fiscale = db.Column(db.String(16), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    data_iscrizione = db.Column(db.Date, default=datetime.utcnow)
    numero_tessera = db.Column(db.String(20), nullable=False, unique=True)

    # Relazione con lo storico prestiti del lettore
    prestiti = db.relationship('Prestito', backref='lettore', lazy=True)

    def __repr__(self):
        return f'<Lettore {self.nome} {self.cognome} ({self.numero_tessera})>'

class Prestito(db.Model):
    __tablename__ = 'prestiti'
    id = db.Column(db.Integer, primary_key=True)
    
    # Importante: Il prestito riguarda la COPIA fisica, non l'OPERA astratta
    id_copia = db.Column(db.Integer, db.ForeignKey('copie.id'), nullable=False)
    id_lettore = db.Column(db.Integer, db.ForeignKey('lettori.id'), nullable=False)
    
    data_prestito = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    data_restituzione = db.Column(db.Date, nullable=True)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Prestito Copia {self.id_copia} - Lettore {self.id_lettore}>'
    

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
    