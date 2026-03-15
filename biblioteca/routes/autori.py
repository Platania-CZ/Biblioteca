from flask import Blueprint, render_template, redirect, url_for, flash, request
from biblioteca import db
from biblioteca.models import Autore, TipoOpera, ClassificazioneDewey
from biblioteca.routes.auth import login_operatore_required

# Definizione del Blueprint
autori_bp = Blueprint('autori', __name__)

# --- ROTTE AUTORI ---
@autori_bp.route('/autori')
@login_operatore_required
def elenco_autori():
    """Visualizza l'elenco di tutti gli autori."""
    items = Autore.query.all()
    return render_template('autori/autori.html', items=items)

@autori_bp.route('/autori/nuovo', methods=['GET', 'POST'])
@login_operatore_required
def nuovo_autore():
    """Crea un nuovo autore."""

    autori = Autore.query.order_by(Autore.cognome).all()
    tipi = TipoOpera.query.order_by(TipoOpera.nome).all()
    classi_dewey = ClassificazioneDewey.query.order_by(ClassificazioneDewey.id).all()

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cognome = request.form.get('cognome', '').strip()
        data_nascita = request.form.get('data_nascita')
        luogo_nascita = request.form.get('luogo_nascita', '').strip()
        note = request.form.get('note', '').strip()

        # Controllo duplicati
        autore_esistente = Autore.query.filter_by(nome=nome, cognome=cognome).first()
        if autore_esistente:
            flash(f"L'autore '{nome} {cognome}' esiste già.", "warning")
            return render_template('autori/autore_form.html', item=None, 
                                 autori_list=autori, tipi_list=tipi, dewey_list=classi_dewey)

        try:
            nuova = Autore(
                nome=nome,
                cognome=cognome,
                data_nascita=data_nascita,
                luogo_nascita=luogo_nascita,
                note=note if note else None
            )
            db.session.add(nuova)
            db.session.commit()
            flash(f"Autore '{nome} {cognome}' creato con successo!", 'success')
            return redirect(url_for('autori.elenco_autori'))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'danger')
        
    return render_template('autori/autore_form.html', item=None, 
                           autori_list=autori, tipi_list=tipi, dewey_list=classi_dewey)

@autori_bp.route('/autori/dettaglio/<int:id>')
@login_operatore_required
def dettaglio_autore(id):
    """Visualizza i dettagli dell'opera e le sue copie."""
    item = Autore.query.get_or_404(id)
    return render_template('autori/autore_dettaglio.html', item=item)

@autori_bp.route('/autori/modifica/<int:id>', methods=['GET', 'POST'])
@login_operatore_required
def modifica_autore(id):
    autore = Autore.query.get_or_404(id)
    if request.method == 'POST':
        try:
            autore.nome = request.form.get('nome', '').strip()
            autore.cognome = request.form.get('cognome', '').strip()
            autore.data_nascita = request.form.get('data_nascita') or None
            autore.luogo_nascita = request.form.get('luogo_nascita', '').strip()
            autore.note = request.form.get('note', '').strip() or None
            db.session.commit()
            flash('Autore aggiornato.', 'info')
            return redirect(url_for('autori.elenco_autori'))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore: {str(e)}', 'danger')
    return render_template('autori/autore_form.html', item=autore)

@autori_bp.route('/autori/elimina/<int:id>', methods=['POST'])
@login_operatore_required
def elimina_autore(id):
    autore = Autore.query.get_or_404(id)
    try:
        db.session.delete(autore)
        db.session.commit()
        flash(f'Autore {autore.nome} {autore.cognome} eliminato.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante eliminazione: {str(e)}', 'danger')
    return redirect(url_for('autori.elenco_autori'))