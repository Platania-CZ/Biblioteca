from flask import Blueprint, render_template, request
from biblioteca.models import Opera, Autore, Copia

# 1. Definizione del Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Pagina principale (Dashboard) con le statistiche della biblioteca."""
    # Recuperiamo alcuni numeri per rendere la home dinamica
    stats = {
        'totale_opere': Opera.query.count(),
        'totale_autori': Autore.query.count(),
        'copie_disponibili': Copia.query.filter_by(stato='Disponibile').count(),
        # Ultime 5 opere aggiunte
        'ultime_opere': Opera.query.order_by(Opera.id.desc()).limit(5).all()
    }
    return render_template('home.html', stats=stats)

@main_bp.route('/cerca')
def cerca():
    """Motore di ricerca globale per titolo o autore."""
    query = request.args.get('q', '').strip()
    risultati = []
    
    if query:
        # Cerchiamo nelle opere per titolo o negli autori per nome/cognome
        risultati = Opera.query.join(Autore).filter(
            (Opera.titolo.contains(query)) | 
            (Autore.nome.contains(query)) | 
            (Autore.cognome.contains(query))
        ).all()
        
    return render_template('risultati_ricerca.html', query=query, risultati=risultati)

@main_bp.route('/contatti')
def contatti():
    """Pagina informativa sui contatti della biblioteca."""
    return render_template('contatti.html')