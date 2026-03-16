from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os

# ==========================================
# INIZIALIZZAZIONE ESTENSIONI
# ==========================================
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = "Effettua il login per accedere a questa pagina."
login_manager.login_message_category = 'info'

def create_app():
    load_dotenv()

    app = Flask(__name__, static_url_path='/static')

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    )
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ==========================================
    # INIZIALIZZAZIONE ESTENSIONI SULL'APP
    # ==========================================
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # ==========================================
    # USER LOADER
    # ==========================================
    @login_manager.user_loader
    def load_user(user_id):
        from biblioteca.models import Utente
        return db.session.get(Utente, int(user_id))

    # ==========================================
    # REGISTRAZIONE BLUEPRINT
    # ==========================================
    from biblioteca.routes.main import main_bp
    from biblioteca.routes.admin import admin_bp
    from biblioteca.routes.auth import auth_bp
    from biblioteca.routes.autori import autori_bp
    from biblioteca.routes.opere import opere_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(autori_bp)
    app.register_blueprint(opere_bp)

    return app