from biblioteca import app, db
from flask import render_template, redirect, url_for, flash, request
from biblioteca.models import Autore, ClassificazioneDewey, Editore, TipoOpera, Opera, Lettore, Prestito, Utente
from biblioteca.forms import RegistrazioneForm, LoginForm
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import and_
from functools import wraps

# ==========================================
# DECORATORI PERSONALIZZATI
# ==========================================

def login_operatore_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Devi effettuare il login per accedere.', 'danger')
            return redirect(url_for('login'))
        if current_user.ruolo not in ['operatore', 'amministratore']:
            flash('Accesso negato.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def login_amministratore_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Devi effettuare il login per accedere.', 'danger')
            return redirect(url_for('login'))
        if not current_user.is_amministratore:
            flash('Accesso negato: solo gli amministratori possono accedere.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# ROUTE PUBBLICHE
# ==========================================

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        utente = Utente.query.filter_by(username=form.username.data).first()
        if utente and utente.check_password_correction(form.password.data):
            login_user(utente)
            flash(f'Benvenuto {utente.username}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Username o password errati.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout effettuato con successo.', 'info')
    return redirect(url_for('home'))

# ==========================================
# ROUTE OPERATORE E AMMINISTRATORE
# ==========================================

@app.route('/opere')
@login_operatore_required
def opere():
    items = Opera.query.all()
    return render_template('opere.html', items=items)

@app.route('/autori')
@login_operatore_required
def autori():
    items = Autore.query.all()
    return render_template('autori.html', items=items)

@app.route('/lettori')
@login_operatore_required
def lettori():
    items = Lettore.query.all()
    return render_template('lettori.html', items=items)

@app.route('/editori')
@login_operatore_required
def editori():
    items = Editore.query.all()
    return render_template('editori.html', items=items)

@app.route('/prestiti')
@login_operatore_required
def prestiti():
    items = Prestito.query.all()
    return render_template('prestiti.html', items=items)

@app.route('/tipi_opere')
@login_operatore_required
def tipi_opere():
    items = TipoOpera.query.all()
    return render_template('tipi_opere.html', items=items)

@app.route('/dewey')
@login_operatore_required
def dewey():
    items = ClassificazioneDewey.query.all()
    return render_template('dewey.html', items=items)

# ==========================================
# ROUTE SOLO AMMINISTRATORE
# ==========================================

@app.route('/registrazione', methods=['GET', 'POST'])
@login_amministratore_required
def registrazione():
    form = RegistrazioneForm()
    if form.validate_on_submit():
        nuovo_utente = Utente(
            username=form.username.data,
            email_address=form.email_address.data,
            ruolo=form.ruolo.data
        )
        nuovo_utente.password = form.password.data
        db.session.add(nuovo_utente)
        db.session.commit()
        flash(f'Utente {nuovo_utente.username} registrato con successo!', 'success')
        return redirect(url_for('home'))
    
    return render_template('registrazione.html', form=form)