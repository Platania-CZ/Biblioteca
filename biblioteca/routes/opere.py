from flask import Blueprint, render_template, redirect, url_for, flash
from biblioteca import db
from biblioteca.models import Autore, ClassificazioneDewey, Opera
from biblioteca.forms import OperaForm
from biblioteca.routes.admin import login_required
from biblioteca.routes.tipo_opera_enum import TipoOperaEnum 

# ==========================================
# DEFINIZIONE BLUEPRINT
# ==========================================
opere_bp = Blueprint('opere', __name__)

# ==========================================
# ROTTE
# ==========================================
@opere_bp.route('/opere')
@login_required
def elenco_opere():
    """Visualizza l'elenco di tutte le opere."""
    items = Opera.query.order_by(Opera.titolo).all()
    return render_template('opere/opere.html', items=items)


@opere_bp.route('/opere/nuova', methods=['GET', 'POST'])
@login_required
def nuova_opera():
    form = OperaForm()
    form.id_autore.choices = [
        (a.id, f'{a.cognome} {a.nome}')
        for a in Autore.query.order_by(Autore.cognome).all()
    ]
    form.id_dewey.choices = [(0, '-- Nessuna --')] + [
        (d.id, d.descrizione_completa)
        for d in ClassificazioneDewey.query.order_by(ClassificazioneDewey.id).all()
    ]
    # tipo_opera non serve choices — li prende da forms.py

    if form.validate_on_submit():
        opera_esistente = Opera.query.filter_by(
            titolo=form.titolo.data,
            id_autore=form.id_autore.data
        ).first()
        if opera_esistente:
            flash(f"L'opera '{form.titolo.data}' per questo autore esiste già.", 'warning')
        else:
            try:
                nuova = Opera(
                    titolo=form.titolo.data,
                    id_autore=form.id_autore.data,
                    tipo_opera=TipoOperaEnum[form.tipo_opera.data],  # ← conversione enum
                    id_dewey=form.id_dewey.data if form.id_dewey.data != 0 else None,
                    isbn_generale=form.isbn_generale.data or None,
                    note=form.note.data or None
                )
                db.session.add(nuova)
                db.session.commit()
                flash(f"Opera '{nuova.titolo}' creata con successo!", 'success')
                return redirect(url_for('opere.elenco_opere'))
            except Exception as e:
                db.session.rollback()
                flash(f'Errore durante il salvataggio: {str(e)}', 'danger')

    return render_template('opere/opera_form.html', form=form, item=None)


@opere_bp.route('/opere/dettaglio/<int:id>')
@login_required
def dettaglio_opera(id):
    """Visualizza i dettagli dell'opera e le sue copie."""
    item = db.get_or_404(Opera, id)
    return render_template('opere/opera_dettaglio.html', item=item)

@opere_bp.route('/opere/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_opera(id):
    opera = db.get_or_404(Opera, id)
    form = OperaForm(obj=opera)
    form.id_autore.choices = [
        (a.id, f'{a.cognome} {a.nome}')
        for a in Autore.query.order_by(Autore.cognome).all()
    ]
    form.id_dewey.choices = [(0, '-- Nessuna --')] + [
        (d.id, d.descrizione_completa)
        for d in ClassificazioneDewey.query.order_by(ClassificazioneDewey.id).all()
    ]

    if form.validate_on_submit():
        try:
            opera.titolo = form.titolo.data
            opera.id_autore = form.id_autore.data
            opera.tipo_opera = TipoOperaEnum[form.tipo_opera.data]  # ← conversione enum
            opera.id_dewey = form.id_dewey.data if form.id_dewey.data != 0 else None
            opera.isbn_generale = form.isbn_generale.data or None
            opera.note = form.note.data or None
            db.session.commit()
            flash('Opera aggiornata con successo.', 'success')
            return redirect(url_for('opere.elenco_opere'))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore: {str(e)}', 'danger')

    return render_template('opere/opera_form.html', form=form, item=opera)


@opere_bp.route('/opere/elimina/<int:id>', methods=['POST'])
@login_required
def elimina_opera(id):
    """Elimina un'opera."""
    opera = db.get_or_404(Opera, id)
    try:
        db.session.delete(opera)
        db.session.commit()
        flash(f"Opera '{opera.titolo}' eliminata.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante eliminazione: {str(e)}', 'danger')
    return redirect(url_for('opere.elenco_opere'))