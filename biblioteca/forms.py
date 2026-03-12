from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from biblioteca.models import Utente

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
        utente = Utente.query.filter_by(username=username.data).first()
        if utente:
            raise ValidationError('Username già in uso, scegline un altro.')

    def validate_email_address(self, email_address):
        utente = Utente.query.filter_by(email_address=email_address.data).first()
        if utente:
            raise ValidationError('Email già in uso, scegline un\'altra.')

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
        if username.data != self.original_username:
            utente = Utente.query.filter_by(username=username.data).first()
            if utente:
                raise ValidationError('Username già in uso, scegline un altro.')

    def validate_email_address(self, email_address):
        if email_address.data != self.original_email:
            utente = Utente.query.filter_by(email_address=email_address.data).first()
            if utente:
                raise ValidationError('Email già in uso, scegline un\'altra.')

class CambioPasswordForm(FlaskForm):
    password_attuale = PasswordField('Password Attuale', validators=[DataRequired()])
    nuova_password = PasswordField('Nuova Password', validators=[DataRequired(), Length(min=6)])
    conferma_password = PasswordField('Conferma Nuova Password', validators=[DataRequired(), EqualTo('nuova_password')])
    submit = SubmitField('Cambia Password')

class CambioPasswordAdminForm(FlaskForm):
    nuova_password = PasswordField('Nuova Password', validators=[DataRequired(), Length(min=6)])
    conferma_password = PasswordField('Conferma Nuova Password', validators=[DataRequired(), EqualTo('nuova_password')])
    submit = SubmitField('Cambia Password')