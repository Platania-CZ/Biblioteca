from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from biblioteca.extensions import db
from biblioteca.models import Opera, Autore, ClassificazioneDewey, Copia, Editore
from biblioteca.forms import OperaForm, CopiaForm
from biblioteca.enums import TipoOperaEnum

# ==========================================
# DEFINIZIONE BLUEPRINT
# ==========================================
opere_bp = Blueprint('opere', __name__)

# ==========================================
# ROTTE OPERE
# ==========================================

@opere_bp.route('/opere')
@login_required
def elenco_opere():
    filtro_titolo = request.args.get('titolo', '').strip()
    filtro_autore = request.args.get('autore', '').strip()
    filtro_tipo = request.args.get('tipo', '').strip()

    query = Opera.query.join(Autore)

    if filtro_titolo:
        query = query.filter(Opera.titolo.ilike(f'%{filtro_titolo}%'))
    if filtro_autore:
        query = query.filter(
            db.or_(
                Autore.nome.ilike(f'%{filtro_autore}%'),
                Autore.cognome.ilike(f'%{filtro_autore}%')
            )
        )
    if filtro_tipo:
        query = query.filter(Opera.tipo_opera == TipoOperaEnum[filtro_tipo])

    items = query.order_by(Opera.titolo).all()

    return render_template('opere/opere.html',
        items=items,
        tipi=TipoOperaEnum,
        filtro_titolo=filtro_titolo,
        filtro_autore=filtro_autore,
        filtro_tipo=filtro_tipo
    )


@opere_bp.route('/opere/nuova', methods=['GET', 'POST'])
@login_required
def nuova_opera():
    """Crea una nuova opera."""
    form = OperaForm()
    form.id_autore.choices = [
        (a.id, f'{a.cognome} {a.nome}')
        for a in Autore.query.order_by(Autore.cognome).all()
    ]
    form.id_dewey.choices = [(0, '-- Nessuna --')] + [
        (d.id, d.descrizione_completa)
        for d in ClassificazioneDewey.query.order_by(ClassificazioneDewey.id).all()
    ]

    if form.validate_on_submit():
        opera_esistente = Opera.query.filter_by(
            titolo=form.titolo.data,
            id_autore=form.id_autore.data
        ).first()
        if opera_esistente:
            flash(f"L'opera '{form.titolo.data}' esiste già — puoi aggiungere una nuova copia.", 'warning')
            return redirect(url_for('opere.nuova_copia', id_opera=opera_esistente.id))
        try:
            nuova = Opera(
                titolo=form.titolo.data,
                id_autore=form.id_autore.data,
                tipo_opera=TipoOperaEnum[form.tipo_opera.data],
                id_dewey=form.id_dewey.data if form.id_dewey.data != 0 else None,
                isbn_generale=form.isbn_generale.data or None,
                note=form.note.data or None
            )
            db.session.add(nuova)
            db.session.commit()
            flash(f"Opera '{nuova.titolo}' creata con successo!", 'success')
            return redirect(url_for('opere.nuova_copia', id_opera=nuova.id))
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
    """Modifica un'opera esistente."""
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
            opera.tipo_opera = TipoOperaEnum[form.tipo_opera.data]
            opera.id_dewey = form.id_dewey.data if form.id_dewey.data != 0 else None
            opera.isbn_generale = form.isbn_generale.data or None
            opera.note = form.note.data or None
            db.session.commit()
            flash('Opera aggiornata con successo.', 'success')
            return redirect(url_for('opere.dettaglio_opera', id=opera.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore: {str(e)}', 'danger')

    return render_template('opere/opera_form.html', form=form, item=opera)


@opere_bp.route('/opere/elimina/<int:id>', methods=['POST'])
@login_required
def elimina_opera(id):
    """Elimina un'opera."""
    opera = db.get_or_404(Opera, id)
    if opera.copie:
        flash('Impossibile eliminare: esistono copie associate. Eliminale prima.', 'danger')
        return redirect(url_for('opere.dettaglio_opera', id=id))
    try:
        db.session.delete(opera)
        db.session.commit()
        flash(f"Opera '{opera.titolo}' eliminata.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante eliminazione: {str(e)}', 'danger')
    return redirect(url_for('opere.elenco_opere'))


# ==========================================
# ROTTE COPIE
# ==========================================
@opere_bp.route('/opere/<int:id_opera>/nuova-copia', methods=['GET', 'POST'])
@login_required
def nuova_copia(id_opera):
    """Aggiunge una nuova copia fisica a un'opera."""
    opera = db.get_or_404(Opera, id_opera)
    form = CopiaForm()
    form.id_editore.choices = [
        (e.id, e.nome)
        for e in Editore.query.order_by(Editore.nome).all()
    ]
    if form.validate_on_submit():
        try:
            copia = Copia(
                id_opera=id_opera,
                id_editore=form.id_editore.data,
                isbn=form.isbn.data or None,
                anno_pubblicazione=form.anno_pubblicazione.data or None,
                posizione_scaffale=form.posizione_scaffale.data or None,
                stato=form.stato.data
            )
            db.session.add(copia)
            db.session.commit()
            flash('Copia aggiunta con successo!', 'success')
            return redirect(url_for('opere.dettaglio_opera', id=id_opera))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'danger')
    return render_template('opere/copia_form.html', form=form, opera=opera, item=None)


@opere_bp.route('/copie/dettaglio/<int:id>')
@login_required
def dettaglio_copia(id):
    """Visualizza i dettagli di una copia."""
    copia = db.get_or_404(Copia, id)
    return render_template('opere/copia_dettaglio.html', item=copia)


@opere_bp.route('/copie/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_copia(id):
    """Modifica una copia esistente."""
    copia = db.get_or_404(Copia, id)
    form = CopiaForm(obj=copia)
    form.id_editore.choices = [
        (e.id, e.nome)
        for e in Editore.query.order_by(Editore.nome).all()
    ]
    if form.validate_on_submit():
        try:
            copia.id_editore = form.id_editore.data
            copia.isbn = form.isbn.data or None
            copia.anno_pubblicazione = form.anno_pubblicazione.data or None
            copia.posizione_scaffale = form.posizione_scaffale.data or None
            copia.stato = form.stato.data
            db.session.commit()
            flash('Copia aggiornata con successo.', 'success')
            return redirect(url_for('opere.dettaglio_opera', id=copia.id_opera))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore: {str(e)}', 'danger')
    return render_template('opere/copia_form.html', form=form, opera=copia.opera, item=copia)


@opere_bp.route('/copie/elimina/<int:id>', methods=['POST'])
@login_required
def elimina_copia(id):
    """Elimina una copia."""
    copia = db.get_or_404(Copia, id)
    id_opera = copia.id_opera
    try:
        db.session.delete(copia)
        db.session.commit()
        flash('Copia eliminata.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante eliminazione: {str(e)}', 'danger')
    return redirect(url_for('opere.dettaglio_opera', id=id_opera))