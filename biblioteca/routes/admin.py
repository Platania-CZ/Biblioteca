from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from biblioteca import db
from biblioteca.models import Utente
from biblioteca.forms import (
    RegistrazioneForm,
    ModificaUtenteForm,
    CambioPasswordForm
)

# ==========================================
# DECORATORE PERSONALIZZATO
# ==========================================
def login_amministratore_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Effettua il login per accedere.', 'info')
            return redirect(url_for('auth.login'))
        if not current_user.is_amministratore:
            flash('Accesso riservato agli amministratori.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# DEFINIZIONE BLUEPRINT
# ==========================================
admin_bp = Blueprint('admin', __name__)

# ==========================================
# ROTTE
# ==========================================
@admin_bp.route('/registrazione', methods=['GET', 'POST'])
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
        flash(f'Utente {nuovo_utente.username} registrato!', 'success')
        return redirect(url_for('admin.gestione_utenti'))
    return render_template('admin/registrazione.html', form=form)


@admin_bp.route('/modifica_utente/<int:utente_id>', methods=['GET', 'POST'])
@login_amministratore_required
def modifica_utente(utente_id):
    utente = db.get_or_404(Utente, utente_id)
    form = ModificaUtenteForm(
        original_username=utente.username,
        original_email=utente.email_address,
        obj=utente
    )
    if form.validate_on_submit():
        utente.username = form.username.data
        utente.email_address = form.email_address.data
        utente.ruolo = form.ruolo.data
        utente.is_amministratore = (form.ruolo.data == 'amministratore')
        db.session.commit()
        flash('Utente modificato!', 'success')
        return redirect(url_for('admin.gestione_utenti'))
    return render_template('admin/modifica_utente.html', form=form, utente=utente)


@admin_bp.route('/cambio-password', methods=['GET', 'POST'])
@login_required
def cambio_password():
    form = CambioPasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password_correction(form.password_attuale.data):
            flash('Password attuale errata.', 'danger')
            return redirect(url_for('admin.cambio_password'))
        current_user.password = form.nuova_password.data
        db.session.commit()
        flash('Password cambiata!', 'success')
        return redirect(url_for('admin.gestione_utenti'))
    return render_template('auth/cambio_password.html', form=form, utente=current_user)


@admin_bp.route('/cambio-password/<int:utente_id>', methods=['GET', 'POST'])
@login_amministratore_required
def cambio_password_admin(utente_id):
    utente = db.get_or_404(Utente, utente_id)
    form = CambioPasswordForm()
    if form.validate_on_submit():
        utente.password = form.nuova_password.data
        db.session.commit()
        flash(f'Password di {utente.username} cambiata!', 'success')
        return redirect(url_for('admin.gestione_utenti'))
    return render_template('auth/cambio_password.html', form=form, utente=utente)


@admin_bp.route('/gestione-utenti')
@login_amministratore_required
def gestione_utenti():
    utenti = Utente.query.all()
    return render_template('admin/gestione_utenti.html', utenti=utenti)