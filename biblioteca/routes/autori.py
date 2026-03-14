from flask import Blueprint, render_template, redirect, url_for, flash, request
from biblioteca import db
from biblioteca.models import Autore, TipoOpera, ClassificazioneDewey, Opera, Editore, Copia
from biblioteca.routes.auth import login_operatore_required
from sqlalchemy import func

# Definizione del Blueprint
opere_bp = Blueprint('opere', __name__)

# --- ROTTE OPERE ---

@opere_bp.route('/opere')
@login_operatore_required
def elenco_opere():
    """Visualizza l'elenco di tutte le opere."""
    items = Opera.query.all()
    return render_template('opere/opere.html', items=items)

@opere_bp.route('/opere/nuova', methods=['GET', 'POST'])
@login_operatore_required
def nuova_opera():
    """Crea una nuova opera con gestione relazioni."""
    autori = Autore.query.order_by(Autore.cognome).all()
    tipi = TipoOpera.query.order_by(TipoOpera.nome).all()
    classi_dewey = ClassificazioneDewey.query.order_by(ClassificazioneDewey.id).all()

    if request.method == 'POST':
        titolo = request.form.get('titolo', '').strip()
        id_autore = request.form.get('id_autore')
        id_tipo_opera = request.form.get('id_tipo_opera')
        id_dewey = request.form.get('id_dewey')
        isbn_generale = request.form.get('isbn_generale', '').strip()
        note = request.form.get('note', '').strip()

        # Controllo duplicati
        opera_esistente = Opera.query.filter_by(titolo=titolo, id_autore=id_autore).first()
        if opera_esistente:
            flash(f"L'opera '{titolo}' per questo autore esiste già.", "warning")
            return render_template('opere/opera_form.html', item=None, 
                                 autori_list=autori, tipi_list=tipi, dewey_list=classi_dewey)

        try:
            nuova = Opera(
                titolo=titolo,
                id_autore=id_autore,
                id_tipo_opera=id_tipo_opera,
                id_dewey=id_dewey if id_dewey else None,
                isbn_generale=isbn_generale if isbn_generale else None,
                note=note if note else None
            )
            db.session.add(nuova)
            db.session.commit()
            flash(f"Opera '{titolo}' creata con successo!", 'success')
            return redirect(url_for('opere.elenco_opere'))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'danger')
        
    return render_template('opere/opera_form.html', item=None, 
                           autori_list=autori, tipi_list=tipi, dewey_list=classi_dewey)

@opere_bp.route('/opere/dettaglio/<int:id>')
@login_operatore_required
def dettaglio_opera(id):
    """Visualizza i dettagli dell'opera e le sue copie."""
    item = Opera.query.get_or_404(id)
    return render_template('opere/opera_dettaglio.html', item=item)

# --- ROTTE TABELLE DI SUPPORTO ---

@opere_bp.route('/editori')
@login_operatore_required
def editori():
    items = Editore.query.all()
    return render_template('editori.html', items=items)

@opere_bp.route('/tipi_opere')
@login_operatore_required
def tipi_opere():
    items = TipoOpera.query.all()
    return render_template('tipi_opere.html', items=items)

@opere_bp.route('/dewey')
@login_operatore_required
def dewey():
    items = ClassificazioneDewey.query.all()
    return render_template('dewey/dewey.html', items=items)