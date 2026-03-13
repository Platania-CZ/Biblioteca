from biblioteca import db, bcrypt
from datetime import datetime
from flask_login import UserMixin
from .nazionalita_enum import NazionalitaEnum  # Importazione relativa
from sqlalchemy import UniqueConstraint # Import necessario

#definizione del modello
class Autore(db.Model):
    __tablename__ = 'autori'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100), nullable=False)
    nazionalita = db.Column(db.Enum(NazionalitaEnum), nullable=False)
    data_nascita = db.Column(db.Date, nullable=True)

    # Definizione del vincolo di unicità sulla coppia nome-cognome
    __table_args__ = (
        UniqueConstraint('nome', 'cognome', name='_nome_cognome_uc'),
    )
    
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
    descrizione_sottosezione = db.Column(db.String(255), nullable=True)

    # Relazione con le opere classificate
    opere = db.relationship('Opera', backref='classificazione', lazy=True)

    @property
    def codice_dewey(self):
        """Restituisce il codice completo formato da sezione principale e sottosezione."""
        if self.sottosezione:
            return f"{self.sezione_principale}.{self.sottosezione}"
        return self.sezione_principale

    @property
    def descrizione_completa(self):
        """Restituisce la descrizione gerarchica (Principale - Sottosezione)."""
        if self.descrizione_sottosezione:
            return f"{self.descrizione} - {self.descrizione_sottosezione}"
        return self.descrizione

    def __repr__(self):
        return f'<ClassificazioneDewey {self.codice_dewey} - {self.descrizione_completa}>'

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
    
class Utente(db.Model, UserMixin):
    __tablename__ = 'Utente'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    ruolo = db.Column(db.Enum('amministratore', 'operatore', name='ruolo_enum'), nullable=False, default='operatore')

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    @property
    def is_amministratore(self):
        return self.ruolo == 'amministratore'

    @property
    def is_operatore(self):
        return self.ruolo == 'operatore'