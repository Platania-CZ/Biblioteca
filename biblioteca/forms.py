from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SelectField,
                     SubmitField, DateField, IntegerField, TextAreaField)
from wtforms.validators import (DataRequired, Email, EqualTo,
                                Length, Optional, ValidationError, NumberRange)
from biblioteca.models import NazionalitaEnum

# ==========================================
# FORM UTENTI
# ==========================================
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Accedi')

class RegistrazioneForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    email_address = StringField('Email', validators=[DataRequired(), Email(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Conferma Password', validators=[DataRequired(), EqualTo('password')])
    ruolo = SelectField('Ruolo', choices=[('operatore', 'Operatore'), ('amministratore', 'Amministratore')])
    submit = SubmitField('Registra')

    def validate_username(self, username):
        from biblioteca.models import Utente
        if Utente.query.filter_by(username=username.data).first():
            raise ValidationError('Username già in uso, scegline un altro.')

    def validate_email_address(self, email_address):
        from biblioteca.models import Utente
        if Utente.query.filter_by(email_address=email_address.data).first():
            raise ValidationError("Email già in uso, scegline un'altra.")

class ModificaUtenteForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    email_address = StringField('Email', validators=[DataRequired(), Email(), Length(max=50)])
    ruolo = SelectField('Ruolo', choices=[('operatore', 'Operatore'), ('amministratore', 'Amministratore')])
    submit = SubmitField('Salva Modifiche')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        from biblioteca.models import Utente
        if username.data != self.original_username:
            if Utente.query.filter_by(username=username.data).first():
                raise ValidationError('Username già in uso, scegline un altro.')

    def validate_email_address(self, email_address):
        from biblioteca.models import Utente
        if email_address.data != self.original_email:
            if Utente.query.filter_by(email_address=email_address.data).first():
                raise ValidationError("Email già in uso, scegline un'altra.")

class CambioPasswordForm(FlaskForm):
    password_attuale = PasswordField('Password Attuale', validators=[DataRequired()])
    nuova_password = PasswordField('Nuova Password', validators=[DataRequired(), Length(min=6)])
    conferma_password = PasswordField('Conferma Nuova Password', validators=[DataRequired(), EqualTo('nuova_password')])
    submit = SubmitField('Cambia Password')

# ==========================================
# FORM AUTORI
# ==========================================
class AutoreForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    cognome = StringField('Cognome', validators=[DataRequired(), Length(max=100)])
    nazionalita = SelectField('Nazionalità',
        choices=[(n.name, n.value) for n in NazionalitaEnum],
        validators=[DataRequired()])
    data_nascita = DateField('Data di Nascita', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Salva')

# ==========================================
# FORM OPERE
# ==========================================
class OperaForm(FlaskForm):
    titolo = StringField('Titolo', validators=[DataRequired(), Length(max=255)])
    id_autore = SelectField('Autore', coerce=int, validators=[DataRequired()])
    id_tipo_opera = SelectField('Tipo Opera', coerce=int, validators=[DataRequired()])
    id_dewey = SelectField('Classificazione Dewey', coerce=int, validators=[Optional()])
    isbn_generale = StringField('ISBN', validators=[Optional(), Length(max=20)])
    note = TextAreaField('Note', validators=[Optional()])
    submit = SubmitField('Salva')

# ==========================================
# FORM COPIE
# ==========================================
class CopiaForm(FlaskForm):
    id_editore = SelectField('Editore', coerce=int, validators=[DataRequired()])
    isbn = StringField('ISBN', validators=[Optional(), Length(max=20)])
    anno_pubblicazione = IntegerField('Anno Pubblicazione', validators=[Optional(), NumberRange(min=1000, max=2100)])
    posizione_scaffale = StringField('Posizione Scaffale', validators=[Optional(), Length(max=50)])
    stato = SelectField('Stato', choices=[
        ('Disponibile', 'Disponibile'),
        ('In prestito', 'In prestito'),
        ('In manutenzione', 'In manutenzione')
    ])
    submit = SubmitField('Salva')

# ==========================================
# FORM LETTORI
# ==========================================
class LettoreForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    cognome = StringField('Cognome', validators=[DataRequired(), Length(max=100)])
    codice_fiscale = StringField('Codice Fiscale', validators=[DataRequired(), Length(min=16, max=16)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=150)])
    telefono = StringField('Telefono', validators=[Optional(), Length(max=20)])
    numero_tessera = StringField('Numero Tessera', validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Salva')

# ==========================================
# FORM PRESTITI
# ==========================================
class PrestitoForm(FlaskForm):
    id_copia = SelectField('Copia', coerce=int, validators=[DataRequired()])
    id_lettore = SelectField('Lettore', coerce=int, validators=[DataRequired()])
    data_prestito = DateField('Data Prestito', format='%Y-%m-%d', validators=[DataRequired()])
    data_restituzione = DateField('Data Restituzione', format='%Y-%m-%d', validators=[Optional()])
    note = TextAreaField('Note', validators=[Optional()])
    submit = SubmitField('Salva')