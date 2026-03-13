from biblioteca import app, db
from flask import render_template, redirect, url_for, flash, request
from biblioteca.models import Autore, ClassificazioneDewey, Editore, TipoOpera, Opera, Lettore, Prestito, Utente
from biblioteca.forms import RegistrazioneForm, LoginForm, ModificaUtenteForm
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import and_, desc,func
from functools import wraps
from .nazionalita_enum import NazionalitaEnum  # Importazione relativa

# ==========================================
# DECORATORI PERSONALIZZATI
# ==========================================

def login_operatore_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Devi effettuare il login per accedere.', 'danger')
            return redirect(url_for('login'))
        if current_user.ruolo not in ['operatore', 'amministratore']:
            flash('Accesso negato.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def login_amministratore_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Devi effettuare il login per accedere.', 'danger')
            return redirect(url_for('login'))
        if not current_user.is_amministratore:
            flash('Accesso negato: solo gli amministratori possono accedere.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# ROUTE PUBBLICHE
# ==========================================

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        utente = Utente.query.filter_by(username=form.username.data).first()
        if utente and utente.check_password_correction(form.password.data):
            login_user(utente)
            flash(f'Benvenuto {utente.username}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Username o password errati.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout effettuato con successo. Arrivederci!', 'info')
    return redirect(url_for('home'))


# ==========================================
# ROUTE OPERATORE E AMMINISTRATORE
# ==========================================

@app.route('/opere')
@login_operatore_required
def opere():
    items = Opera.query.all()
    return render_template('opere.html', items=items)

@app.route('/autori')
@login_operatore_required
def autori():
    # Il query.all() va bene, l'ordinamento con func.lower è corretto per rendere
    # l'ordine alfabetico indipendente dalle maiuscole/minuscole
    items = Autore.query.order_by(func.lower(Autore.cognome), func.lower(Autore.nome)).all()
    
    # Passiamo anche NazionalitaEnum se nel template autori.html 
    # hai filtri o modali che richiedono la lista delle nazioni
    return render_template('autori.html', items=items, NazionalitaEnum=NazionalitaEnum)

@app.route('/autori/nuovo', methods=['GET', 'POST'])
@login_operatore_required
def nuovo_autore():
    """Gestisce la creazione di un nuovo autore con controllo duplicati e pulizia dati."""
    if request.method == 'POST':
        # Recuperiamo e puliamo i dati con .strip()
        nome = request.form.get('nome', '').strip()
        cognome = request.form.get('cognome', '').strip()
        nazionalita_str = request.form.get('nazionalita')
        
        # 1. Controllo preventivo duplicati (Nome + Cognome)
        autore_esistente = Autore.query.filter_by(nome=nome, cognome=cognome).first()
        if autore_esistente:
            flash(f"L'autore {nome} {cognome} esiste già nel database.", "warning")
            return render_template('autore_form.html', item=None, NazionalitaEnum=NazionalitaEnum)

        try:
            # 2. Conversione della stringa in oggetto Enum
            nazionalita_obj = NazionalitaEnum(nazionalita_str)
            
            # 3. Creazione del nuovo record
            nuovo = Autore(
                nome=nome, 
                cognome=cognome, 
                nazionalita=nazionalita_obj
            )
            
            db.session.add(nuovo)
            db.session.commit()
            
            flash('Autore creato con successo!', 'success')
            return redirect(url_for('autori'))
            
        except ValueError:
            flash('Nazionalità non valida selezionata.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'danger')
        
    return render_template('autore_form.html', item=None, NazionalitaEnum=NazionalitaEnum)

@app.route('/autori/dettaglio/<int:id>')
@login_operatore_required
def dettaglio_autore(id):
    """Visualizza i dettagli di un singolo autore."""
    # Recupera l'autore o restituisce errore 404 se non esiste
    autore = Autore.query.get_or_404(id)
    
    return render_template('autore_dettaglio.html', 
                           item=autore, 
                           NazionalitaEnum=NazionalitaEnum)

@app.route('/autori/modifica/<int:id>', methods=['GET', 'POST'])
@login_operatore_required
def modifica_autore(id):
    """Gestisce la modifica di un autore esistente con controllo duplicati."""
    autore = Autore.query.get_or_404(id)
    
    if request.method == 'POST':
        # 1. Recupero e pulizia dati
        nuovo_nome = request.form.get('nome', '').strip()
        nuovo_cognome = request.form.get('cognome', '').strip()
        nazionalita_str = request.form.get('nazionalita')
        
        # 2. Controllo duplicati: cerchiamo un autore con lo stesso nome e cognome
        # MA che abbia un ID diverso da quello che stiamo modificando
        duplicato = Autore.query.filter(
            Autore.nome == nuovo_nome, 
            Autore.cognome == nuovo_cognome, 
            Autore.id != id
        ).first()
        
        if duplicato:
            flash(f"Esiste già un altro autore registrato come {nuovo_nome} {nuovo_cognome}!", "warning")
            return render_template('autore_form.html', item=autore, NazionalitaEnum=NazionalitaEnum)

        try:
            # 3. Aggiornamento campi
            autore.nome = nuovo_nome
            autore.cognome = nuovo_cognome
            autore.nazionalita = NazionalitaEnum(nazionalita_str)
            
            db.session.commit()
            flash('Autore aggiornato con successo!', 'info')
            return redirect(url_for('autori'))
            
        except ValueError:
            flash('Errore: Nazionalità non valida selezionata.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante l\'aggiornamento: {str(e)}', 'danger')
        
    return render_template('autore_form.html', item=autore, NazionalitaEnum=NazionalitaEnum)

@app.route('/autori/elimina/<int:id>', methods=['POST'])
@login_operatore_required
def elimina_autore(id):
    """Elimina un autore dal database."""
    autore = Autore.query.get_or_404(id)
    db.session.delete(autore)
    db.session.commit()
    flash('Autore eliminato.', 'danger')
    return redirect(url_for('autori'))

@app.route('/lettori')
@login_operatore_required
def lettori():
    items = Lettore.query.all()
    return render_template('lettori.html', items=items)

@app.route('/editori')
@login_operatore_required
def editori():
    items = Editore.query.all()
    return render_template('editori.html', items=items)

@app.route('/prestiti')
@login_operatore_required
def prestiti():
    items = Prestito.query.all()
    return render_template('prestiti.html', items=items)

@app.route('/tipi_opere')
@login_operatore_required
def tipi_opere():
    items = TipoOpera.query.all()
    return render_template('tipi_opere.html', items=items)

@app.route('/dewey')
@login_operatore_required
def dewey():
    items = ClassificazioneDewey.query.all()
    return render_template('dewey.html', items=items)

# solo amministratore
@app.route('/registrazione', methods=['GET', 'POST'])
@login_amministratore_required
def registrazione():
    form = RegistrazioneForm()
    if form.validate_on_submit():
        nuovo_utente = Utente(
            username=form.username.data,
            email_address=form.email_address.data,
            ruolo=form.ruolo.data
        )
        nuovo_utente.password = form.password.data
        db.session.add(nuovo_utente)
        db.session.commit()
        flash(f'Utente {nuovo_utente.username} registrato con successo!', 'success')
        return redirect(url_for('home'))
    
    return render_template('registrazione.html', form=form)

@app.route('/modifica_utente/<int:utente_id>', methods=['GET', 'POST'])
@login_amministratore_required
def modifica_utente(utente_id):
    utente = Utente.query.get_or_404(utente_id)

    # Inizializza la form con i valori originali per la validazione
    form = ModificaUtenteForm(
        original_username=utente.username,
        original_email=utente.email_address,
        obj=utente
    )

    if form.validate_on_submit():
        utente.username = form.username.data
        utente.email_address = form.email_address.data
        utente.ruolo = form.ruolo.data
        utente.is_amministratore = (form.ruolo.data == 'amministratore')

        db.session.commit()
        flash(f'Utente {utente.username} modificato con successo!', 'success')
        return redirect(url_for('gestione_utenti'))

    return render_template('modifica_utente.html', form=form, utente=utente)


# Cambio password proprio account (operatore e amministratore)
@app.route('/cambio-password', methods=['GET', 'POST'])
@login_required
def cambio_password():
    from biblioteca.forms import CambioPasswordForm
    form = CambioPasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password_correction(form.password_attuale.data):
            flash('Password attuale errata.', 'danger')
            return redirect(url_for('cambio_password'))
        current_user.password = form.nuova_password.data
        db.session.commit()
        flash('Password cambiata con successo!', 'success')
        return redirect(url_for('home'))
    return render_template('cambio_password.html', form=form, utente=current_user)

# Cambio password altrui (solo amministratore)
@app.route('/cambio-password/<int:utente_id>', methods=['GET', 'POST'])
@login_amministratore_required
def cambio_password_admin(utente_id):
    from biblioteca.forms import CambioPasswordAdminForm
    utente = Utente.query.get_or_404(utente_id)
    form = CambioPasswordAdminForm()
    if form.validate_on_submit():
        utente.password = form.nuova_password.data
        db.session.commit()
        flash(f'Password di {utente.username} cambiata con successo!', 'success')
        return redirect(url_for('gestione_utenti'))
    return render_template('cambio_password.html', form=form, utente=utente)

# Lista utenti (solo amministratore)
@app.route('/gestione-utenti')
@login_amministratore_required
def gestione_utenti():
    utenti = Utente.query.all()
    return render_template('gestione_utenti.html', utenti=utenti)