from flask import Blueprint, render_template
from biblioteca.models import Opera, Autore, Copia, Editore, TipoOpera, ClassificazioneDewey
from biblioteca.routes.auth import login_operatore_required

# 1. Definizione del Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Pagina principale (Dashboard) con le statistiche della biblioteca."""
    # Recuperiamo alcuni numeri per rendere la home dinamica
    stats = {
        'totale_opere': Opera.query.count(),
        'totale_autori': Autore.query.count(),
        'copie_disponibili': Copia.query.filter_by(stato='Disponibile').count(),
        # Ultime 5 opere aggiunte
        'ultime_opere': Opera.query.order_by(Opera.id.desc()).limit(5).all()
    }
    return render_template('home.html', stats=stats)





main_bp.route('/editori')
@login_operatore_required
def editori():
    items = Editore.query.all()
    return render_template('editori/editori.html', items=items)

@main_bp.route('/tipi_opere')
@login_operatore_required
def tipi_opere():
    items = TipoOpera.query.all()
    return render_template('tipi_opere.html', items=items)

@main_bp.route('/dewey')
@login_operatore_required
def dewey():
    items = ClassificazioneDewey.query.all()
    return render_template('dewey/dewey.html', items=items)