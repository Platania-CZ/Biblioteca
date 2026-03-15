from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# 1. Inizializzazione delle estensioni
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Configurazione globale per Flask-Login
# 'gestione.login' perché la rotta login ora è dentro il blueprint gestione_bp
login_manager.login_view = 'auth.login'
login_manager.login_message = "Effettua il login per accedere a questa pagina."
login_manager.login_message_category = 'info'

def create_app():
    """Factory per la creazione dell'applicazione Flask."""
    load_dotenv()
    
    app = Flask(__name__, static_url_path='/static')

    # Configurazione tramite variabili d'ambiente
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    )
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 2. Inizializzazione delle estensioni sull'app creata
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # 3. User Loader per Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from biblioteca.models import Utente
        return Utente.query.get(int(user_id))

    # 4. Registrazione dei Blueprints
    # Importiamo i blueprint dai nuovi percorsi nella cartella routes/
    from biblioteca.routes.main import main_bp
    from biblioteca.routes.admin import admin_bp
    from biblioteca.routes.auth import auth_bp
    from biblioteca.routes.autori import autori_bp
    from biblioteca.routes.opere import opere_bp

    # Registrazione
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(autori_bp)
    app.register_blueprint(opere_bp)

    return app