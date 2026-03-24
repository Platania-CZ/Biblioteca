from flask import Blueprint, render_template, redirect, url_for, flash, request
from biblioteca.extensions import db
from biblioteca.models import Autore, NazionalitaEnum
from biblioteca.forms import AutoreForm
from biblioteca.blueprints.admin.routes import login_required

autori_bp = Blueprint('autori', __name__)

@autori_bp.route('/autori')
@login_required
def elenco_autori():
    filtro_cognome = request.args.get('cognome', '').strip()
    filtro_nome = request.args.get('nome', '').strip()
    filtro_nazionalita = request.args.get('nazionalita', '').strip()
    page = request.args.get('page', 1, type=int)          # ✅ aggiunto

    query = Autore.query

    if filtro_cognome:
        query = query.filter(Autore.cognome.ilike(f'%{filtro_cognome}%'))
    if filtro_nome:
        query = query.filter(Autore.nome.ilike(f'%{filtro_nome}%'))
    if filtro_nazionalita:
        query = query.filter(Autore.nazionalita == NazionalitaEnum[filtro_nazionalita])

    items = query.order_by(Autore.cognome).paginate(page=page, per_page=10, error_out=False)  # ✅ aggiunto

    return render_template('autori/autori.html',
        items=items,
        total=items.total,                                 # ✅ aggiunto
        nazionalita_enum=NazionalitaEnum,
        filtro_cognome=filtro_cognome,
        filtro_nome=filtro_nome,
        filtro_nazionalita=filtro_nazionalita
    )

@autori_bp.route('/autori/nuovo', methods=['GET', 'POST'])
@login_required
def nuovo_autore():
    form = AutoreForm()
    if form.validate_on_submit():
        autore_esistente = Autore.query.filter_by(
            nome=form.nome.data,
            cognome=form.cognome.data
        ).first()
        if autore_esistente:
            flash(f"L'autore '{form.nome.data} {form.cognome.data}' esiste già.", 'warning')
        else:
            try:
                nuovo = Autore(
                    nome=form.nome.data,
                    cognome=form.cognome.data,
                    nazionalita=form.nazionalita.data,
                    data_nascita=form.data_nascita.data
                )
                db.session.add(nuovo)
                db.session.commit()
                flash(f"Autore '{nuovo.nome} {nuovo.cognome}' creato con successo!", 'success')
                return redirect(url_for('autori.elenco_autori'))
            except Exception as e:
                db.session.rollback()
                flash(f'Errore durante il salvataggio: {str(e)}', 'danger')
    return render_template('autori/autore_form.html', form=form, item=None)

@autori_bp.route('/autori/dettaglio/<int:id>')
@login_required
def dettaglio_autore(id):
    item = db.get_or_404(Autore, id)
    return render_template('autori/autore_dettaglio.html', item=item)

@autori_bp.route('/autori/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_autore(id):
    autore = db.get_or_404(Autore, id)
    form = AutoreForm(obj=autore)
    if form.validate_on_submit():
        try:
            autore.nome = form.nome.data
            autore.cognome = form.cognome.data
            autore.nazionalita = form.nazionalita.data
            autore.data_nascita = form.data_nascita.data
            db.session.commit()
            flash('Autore aggiornato con successo.', 'success')
            return redirect(url_for('autori.elenco_autori'))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore: {str(e)}', 'danger')
    return render_template('autori/autore_form.html', form=form, item=autore)

@autori_bp.route('/autori/elimina/<int:id>', methods=['POST'])
@login_required
def elimina_autore(id):
    autore = db.get_or_404(Autore, id)
    if autore.opere:
        flash(f'Impossibile eliminare: {autore.nome} {autore.cognome} ha {len(autore.opere)} opere associate. Eliminale prima.', 'danger')
        return redirect(url_for('autori.dettaglio_autore', id=id))
    try:
        db.session.delete(autore)
        db.session.commit()
        flash(f'Autore {autore.nome} {autore.cognome} eliminato.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante eliminazione: {str(e)}', 'danger')
    return redirect(url_for('autori.elenco_autori'))