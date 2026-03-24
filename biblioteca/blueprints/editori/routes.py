from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from biblioteca.extensions import db
from biblioteca.models import Editore
from biblioteca.forms import EditoreForm

# ==========================================
# DEFINIZIONE BLUEPRINT
# ==========================================
editori_bp = Blueprint('editori', __name__)

# ==========================================
# ROTTE
# ==========================================
@editori_bp.route('/editori')
@login_required
def elenco_editori():
    filtro_nome = request.args.get('nome', '').strip()
    filtro_sede = request.args.get('sede', '').strip()
    page = request.args.get('page', 1, type=int)          # ✅ aggiunto

    query = Editore.query

    if filtro_nome:
        query = query.filter(Editore.nome.ilike(f'%{filtro_nome}%'))
    if filtro_sede:
        query = query.filter(Editore.sede.ilike(f'%{filtro_sede}%'))

    items = query.order_by(Editore.nome).all()

    items = query.order_by(Editore.nome).paginate(page=page, per_page=10, error_out=False)  # ✅ aggiunto

    return render_template('editori/editori.html',
        items=items,
        total=items.total,                                 # ✅ aggiunto
        filtro_nome=filtro_nome,
        filtro_sede=filtro_sede
    )


@editori_bp.route('/editori/nuovo', methods=['GET', 'POST'])
@login_required
def nuovo_editore():
    """Crea un nuovo editore."""
    form = EditoreForm()
    if form.validate_on_submit():
        esistente = Editore.query.filter_by(nome=form.nome.data).first()
        if esistente:
            flash(f"L'editore '{form.nome.data}' esiste già.", 'warning')
        else:
            try:
                editore = Editore(
                    nome=form.nome.data,
                    sede=form.sede.data or None
                )
                db.session.add(editore)
                db.session.commit()
                flash(f"Editore '{editore.nome}' creato con successo!", 'success')
                return redirect(url_for('editori.elenco_editori'))
            except Exception as e:
                db.session.rollback()
                flash(f'Errore durante il salvataggio: {str(e)}', 'danger')
    return render_template('editori/editore_form.html', form=form, item=None)


@editori_bp.route('/editori/dettaglio/<int:id>')
@login_required
def dettaglio_editore(id):
    """Visualizza i dettagli di un editore."""
    item = db.get_or_404(Editore, id)
    return render_template('editori/editore_dettaglio.html', item=item)


@editori_bp.route('/editori/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_editore(id):
    """Modifica un editore esistente."""
    editore = db.get_or_404(Editore, id)
    form = EditoreForm(obj=editore)
    if form.validate_on_submit():
        esistente = Editore.query.filter_by(nome=form.nome.data).first()
        if esistente and esistente.id != editore.id:
            flash(f"L'editore '{form.nome.data}' esiste già.", 'warning')
        else:
            try:
                editore.nome = form.nome.data
                editore.sede = form.sede.data or None
                db.session.commit()
                flash('Editore aggiornato con successo.', 'success')
                return redirect(url_for('editori.elenco_editori'))
            except Exception as e:
                db.session.rollback()
                flash(f'Errore: {str(e)}', 'danger')
    return render_template('editori/editore_form.html', form=form, item=editore)


@editori_bp.route('/editori/elimina/<int:id>', methods=['POST'])
@login_required
def elimina_editore(id):
    """Elimina un editore."""
    editore = db.get_or_404(Editore, id)
    if editore.copie:
        flash('Impossibile eliminare: esistono copie associate a questo editore.', 'danger')
        return redirect(url_for('editori.dettaglio_editore', id=id))
    try:
        db.session.delete(editore)
        db.session.commit()
        flash(f"Editore '{editore.nome}' eliminato.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante eliminazione: {str(e)}', 'danger')
    return redirect(url_for('editori.elenco_editori'))