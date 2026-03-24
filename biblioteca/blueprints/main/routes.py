from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from biblioteca.extensions import db
from biblioteca.models import Opera, Autore, Copia, Editore, ClassificazioneDewey

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('home.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    from biblioteca.models import Prestito, Utente
    stats = {
        'totale_opere': Opera.query.count(),
        'totale_autori': Autore.query.count(),
        'totale_editori': Editore.query.count(),
        'totale_copie': Copia.query.count(),
        'copie_disponibili': Copia.query.filter_by(stato='Disponibile').count(),
        'copie_in_prestito': Copia.query.filter_by(stato='In prestito').count(),
        'totale_prestiti': Prestito.query.count(),
        'prestiti_aperti': Prestito.query.filter_by(data_restituzione=None).count(),
        'ultime_opere': Opera.query.order_by(Opera.id.desc()).limit(5).all(),
        'totale_utenti': Utente.query.count(),
        'totale_operatori': Utente.query.filter_by(ruolo='operatore').count(),
        'totale_amministratori': Utente.query.filter_by(ruolo='amministratore').count(),
    }
    return render_template('dashboard.html', stats=stats)
