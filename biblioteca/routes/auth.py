from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from biblioteca import bcrypt
from biblioteca.models import Utente
from functools import wraps

# 1. Definizione del Blueprint
auth_bp = Blueprint('auth', __name__)

# 2. Decoratore Personalizzato
def login_operatore_required(f):
    """
    Verifica che l'utente non solo sia loggato, ma abbia anche il ruolo di 'operatore'.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # Assumendo che il tuo modello Utente abbia un campo 'ruolo'
        # o che tu voglia semplicemente limitare l'accesso ai loggati
        if not current_user.is_authenticated:
             return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# 3. Rotte di Autenticazione
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Gestisce l'accesso dell'operatore."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        utente = Utente.query.filter_by(email=email).first()
        
        # Verifica se l'utente esiste e la password è corretta
        if utente and bcrypt.check_password_hash(utente.password, password):
            login_user(utente)
            next_page = request.args.get('next') # Per tornare alla pagina che l'utente voleva visitare
            flash(f'Bentornato, {utente.nome}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login non riuscito. Controlla email e password.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Gestisce l'uscita dell'utente."""
    logout_user()
    flash('Sei stato disconnesso correttamente.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profilo')
@login_required
def profilo():
    """Visualizza i dati dell'operatore loggato."""
    return render_template('auth/profilo.html', utente=current_user)