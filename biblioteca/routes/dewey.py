from flask import Blueprint, render_template, request
from flask_login import login_required
from biblioteca import db
from biblioteca.models import ClassificazioneDewey

# ==========================================
# DEFINIZIONE BLUEPRINT
# ==========================================
dewey_bp = Blueprint('dewey', __name__)

# ==========================================
# ROTTE
# ==========================================
@dewey_bp.route('/dewey')
@login_required
def dewey():
    """Visualizza la classificazione Dewey con filtri."""
    filtro_sezione = request.args.get('sezione', '').strip()
    filtro_descrizione = request.args.get('descrizione', '').strip()

    query = ClassificazioneDewey.query

    if filtro_sezione:
        query = query.filter(
            ClassificazioneDewey.sezione_principale.ilike(f'%{filtro_sezione}%')
        )
    if filtro_descrizione:
        query = query.filter(
            db.or_(
                ClassificazioneDewey.descrizione.ilike(f'%{filtro_descrizione}%'),
                ClassificazioneDewey.descrizione_sottosezione.ilike(f'%{filtro_descrizione}%')
            )
        )

    items = query.order_by(
        ClassificazioneDewey.sezione_principale,
        ClassificazioneDewey.sottosezione
    ).all()

    return render_template('dewey/dewey.html',
        items=items,
        filtro_sezione=filtro_sezione,
        filtro_descrizione=filtro_descrizione
    )