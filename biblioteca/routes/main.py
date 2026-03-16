from flask import Blueprint, render_template
from flask_login import login_required
from biblioteca.models import Opera, Autore, Copia, Editore 
from biblioteca.routes.tipo_opera_enum import TipoOperaEnum

# ==========================================
# DEFINIZIONE BLUEPRINT
# ==========================================
main_bp = Blueprint('main', __name__)

# ==========================================
# ROTTE
# ==========================================
@main_bp.route('/')
def index():
    """Pagina principale (Dashboard) con le statistiche della biblioteca."""
    stats = {
        'totale_opere': Opera.query.count(),
        'totale_autori': Autore.query.count(),
        'copie_disponibili': Copia.query.filter_by(stato='Disponibile').count(),
        'ultime_opere': Opera.query.order_by(Opera.id.desc()).limit(5).all()
    }
    return render_template('home.html', stats=stats)


@main_bp.route('/editori')
@login_required
def editori():
    items = Editore.query.all()
    return render_template('editori/editori.html', items=items)


@main_bp.route('/tipi_opere')
@login_required
def tipi_opere():
    return render_template('tipi_opere.html', tipi=TipoOperaEnum)

