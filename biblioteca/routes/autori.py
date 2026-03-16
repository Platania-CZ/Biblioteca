from flask import Blueprint, render_template, redirect, url_for, flash
from biblioteca import db
from biblioteca.models import Autore
from biblioteca.forms import AutoreForm
from biblioteca.routes.admin import login_required

# ==========================================
# DEFINIZIONE BLUEPRINT
# ==========================================
autori_bp = Blueprint('autori', __name__)

# ==========================================
# ROTTE
# ==========================================
@autori_bp.route('/autori')
@login_required
def elenco_autori():
    """Visualizza l'elenco di tutti gli autori."""
    items = Autore.query.order_by(Autore.cognome).all()
    return render_template('autori/autori.html', items=items)


@autori_bp.route('/autori/nuovo', methods=['GET', 'POST'])
@login_required
def nuovo_autore():
    """Crea un nuovo autore."""
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
    """Visualizza i dettagli dell'autore."""
    item = db.get_or_404(Autore, id)
    return render_template('autori/autore_dettaglio.html', item=item)


@autori_bp.route('/autori/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_autore(id):
    """Modifica un autore esistente."""
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
    """Elimina un autore."""
    autore = db.get_or_404(Autore, id)
    try:
        db.session.delete(autore)
        db.session.commit()
        flash(f'Autore {autore.nome} {autore.cognome} eliminato.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante eliminazione: {str(e)}', 'danger')
    return redirect(url_for('autori.elenco_autori'))