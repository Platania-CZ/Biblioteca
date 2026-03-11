from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/bibliotecaDb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==========================================
# DEFINIZIONE DEI MODELLI
# ==========================================

class Autore(db.Model):
    __tablename__ = 'autori'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100), nullable=False)
    nazionalita = db.Column(db.String(100), nullable=False)
    data_nascita = db.Column(db.Date, nullable=True)

    # Uso della stringa 'Opera' per evitare errori di caricamento
    opere = db.relationship('Opera', back_populates='autore')
    
    def __repr__(self):
        return f'<Autore {self.nome} {self.cognome}>'

class Editore(db.Model):
    __tablename__ = 'editori'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    sede = db.Column(db.String(100), nullable=True)

    copie = db.relationship('Copia', backref='editore', lazy=True)

    def __repr__(self):
        return f'<Editore {self.nome}>'

class TipoOpera(db.Model):
    __tablename__ = 'tipi_opere'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False) 

    opere = db.relationship('Opera', backref='tipo', lazy=True)

    def __repr__(self):
        return f'<TipoOpera {self.nome}>'

class ClassificazioneDewey(db.Model):
    __tablename__ = 'classificazione_dewey'
    id = db.Column(db.Integer, primary_key=True)
    descrizione = db.Column(db.String(255), nullable=False)
    sezione_principale = db.Column(db.String(3), nullable=False)
    sottosezione = db.Column(db.String(20), nullable=True)

    opere = db.relationship('Opera', backref='classificazione', lazy=True)

    @property
    def codice_dewey(self):
        if self.sottosezione:
            return f"{self.sezione_principale}.{self.sottosezione}"
        return self.sezione_principale

    def __repr__(self):
        return f'<ClassificazioneDewey {self.codice_dewey} - {self.descrizione}>'

class Opera(db.Model):
    __tablename__ = 'opere'
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(255), nullable=False)
    
    id_autore = db.Column(db.Integer, db.ForeignKey('autori.id'), nullable=False)
    id_tipo_opera = db.Column(db.Integer, db.ForeignKey('tipi_opere.id'), nullable=False)
    id_dewey = db.Column(db.Integer, db.ForeignKey('classificazione_dewey.id'), nullable=True)
    
    isbn_generale = db.Column(db.String(20), nullable=True)
    note = db.Column(db.Text, nullable=True)

    autore = db.relationship('Autore', back_populates='opere')
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

    prestiti = db.relationship('Prestito', backref='copia', lazy=True)

    def __repr__(self):
        # Nota: usiamo self.opera.titolo solo se la relazione è caricata
        return f'<Copia ID {self.id}>'

class Lettore(db.Model):
    __tablename__ = 'lettori'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100), nullable=False)
    codice_fiscale = db.Column(db.String(16), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    # FIX: Passiamo la funzione utcnow senza parentesi
    data_iscrizione = db.Column(db.Date, default=datetime.utcnow)
    numero_tessera = db.Column(db.String(20), nullable=False, unique=True)

    prestiti = db.relationship('Prestito', backref='lettore', lazy=True)

    def __repr__(self):
        return f'<Lettore {self.nome} {self.cognome}>'

class Prestito(db.Model):
    __tablename__ = 'prestiti'
    id = db.Column(db.Integer, primary_key=True)
    id_copia = db.Column(db.Integer, db.ForeignKey('copie.id'), nullable=False)
    id_lettore = db.Column(db.Integer, db.ForeignKey('lettori.id'), nullable=False)
    
    # FIX: Passiamo la funzione utcnow senza parentesi
    data_prestito = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    data_restituzione = db.Column(db.Date, nullable=True)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Prestito Copia {self.id_copia}>'

# ==========================================
# CREAZIONE TABELLE E POPOLAMENTO DEWEY
# ==========================================

with app.app_context():
    # 1. Creiamo tutte le tabelle (SQLAlchemy gestisce l'ordine corretto delle FK)
    db.create_all()
    
    # 2. Popolamento Dewey (solo se la tabella è vuota)
    if ClassificazioneDewey.query.count() == 0:
        print("Popolamento classificazione Dewey in corso...")
        dewey_data = {
            '000': [(None, 'Generalità'), ('010', 'Bibliografia'), ('020', 'Biblioteconomia'), ('030', 'Enciclopedie'), ('050', 'Pubblicazioni seriali'), ('060', 'Museologia'), ('070', 'Giornalismo'), ('080', 'Raccolte generali'), ('090', 'Libri rari')],
            '100': [(None, 'Filosofia e psicologia'), ('110', 'Metafisica'), ('120', 'Gnoseologia'), ('130', 'Paranormale'), ('140', 'Scuole filosofiche'), ('150', 'Psicologia'), ('160', 'Logica'), ('170', 'Etica'), ('180', 'Filosofia antica'), ('190', 'Filosofia moderna')],
            '200': [(None, 'Religione'), ('210', 'Filosofia della religione'), ('220', 'Bibbia'), ('230', 'Teologia cristiana'), ('240', 'Morale cristiana'), ('250', 'Ordini religiosi'), ('260', 'Ecclesiologia'), ('270', 'Storia della Chiesa'), ('280', 'Confessioni cristiane'), ('290', 'Altre religioni')],
            '300': [(None, 'Scienze sociali'), ('310', 'Statistica'), ('320', 'Scienza politica'), ('330', 'Economia'), ('340', 'Diritto'), ('350', 'Amministrazione pubblica'), ('360', 'Problemi sociali'), ('370', 'Educazione'), ('380', 'Commercio'), ('390', 'Costumi e folclore')],
            '400': [(None, 'Lingue'), ('410', 'Linguistica'), ('420', 'Inglese'), ('430', 'Lingue germaniche'), ('440', 'Lingue romanze'), ('450', 'Italiano'), ('460', 'Spagnolo e portoghese'), ('470', 'Latino'), ('480', 'Greco classico'), ('490', 'Altre lingue')],
            '500': [(None, 'Scienze pure'), ('510', 'Matematica'), ('520', 'Astronomia'), ('530', 'Fisica'), ('540', 'Chimica'), ('550', 'Scienze della terra'), ('560', 'Paleontologia'), ('570', 'Biologia'), ('580', 'Botanica'), ('590', 'Zoologia')],
            '600': [(None, 'Tecnologia'), ('610', 'Medicina'), ('620', 'Ingegneria'), ('630', 'Agricoltura'), ('640', 'Economia domestica'), ('650', 'Management'), ('660', 'Ingegneria chimica'), ('670', 'Manifattura'), ('680', 'Lavorazioni speciali'), ('690', 'Edilizia')],
            '700': [(None, 'Arti e sport'), ('710', 'Urbanistica'), ('720', 'Architettura'), ('730', 'Scultura'), ('740', 'Disegno'), ('750', 'Pittura'), ('760', 'Grafica'), ('770', 'Fotografia'), ('780', 'Musica'), ('790', 'Spettacolo e sport')],
            '800': [(None, 'Letteratura'), ('810', 'Letteratura americana'), ('820', 'Letteratura inglese'), ('830', 'Letterature germaniche'), ('840', 'Letterature romanze'), ('850', 'Letteratura italiana'), ('860', 'Letterature ispaniche'), ('870', 'Letteratura latina'), ('880', 'Letteratura greca'), ('890', 'Altre letterature')],
            '900': [(None, 'Storia e geografia'), ('910', 'Geografia e viaggi'), ('920', 'Biografia e genealogia'), ('930', 'Storia antica'), ('940', 'Storia d\'Europa'), ('950', 'Storia d\'Asia'), ('960', 'Storia d\'Africa'), ('970', 'Storia del Nord America'), ('980', 'Storia del Sud America'), ('990', 'Storia di altre aree')]
        }

        for principale, sottosezioni in dewey_data.items():
            for codice_full, desc in sottosezioni:
                sotto_codice = codice_full[1:] if codice_full else None
                entry = ClassificazioneDewey(
                    sezione_principale=principale,
                    sottosezione=sotto_codice,
                    descrizione=desc
                )
                db.session.add(entry)
        
        db.session.commit()
        print("Database e Dewey pronti!")

