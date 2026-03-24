from flask import Blueprint, render_template, request
from flask_login import login_required
from biblioteca.extensions import db
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
    page = request.args.get('page', 1, type=int)          # ✅ aggiunto

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

    items = query.order_by(ClassificazioneDewey.sezione_principale).paginate(page=page, per_page=10, error_out=False)  # ✅ aggiunto

    return render_template('dewey/dewey.html',
        items=items,
        total=items.total,                                 # ✅ aggiunto
        filtro_sezione=filtro_sezione,
        filtro_descrizione=filtro_descrizione
    )