from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from biblioteca.models import Utente
from biblioteca.forms import LoginForm

# ==========================================
# DEFINIZIONE BLUEPRINT
# ==========================================
auth_bp = Blueprint('auth', __name__)

# ==========================================
# ROTTE
# ==========================================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Gestisce l'accesso dell'utente."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        utente = Utente.query.filter_by(username=form.username.data).first()
        if utente and utente.check_password_correction(form.password.data):
            login_user(utente)
            next_page = request.args.get('next')
            flash(f'Bentornato, {utente.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login non riuscito. Controlla username e password.', 'danger')

    return render_template('auth/login.html', form=form)


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
    """Visualizza i dati dell'utente loggato."""
    return render_template('auth/profilo.html', utente=current_user)