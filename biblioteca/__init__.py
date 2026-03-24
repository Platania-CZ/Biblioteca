from flask import Flask
from dotenv import load_dotenv
from biblioteca.extensions import db, bcrypt, login_manager, csrf, migrate
import os

def create_app():
    load_dotenv()

    app = Flask(__name__, static_url_path='/static')

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    )
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)      # ✅ aggiunto

    @login_manager.user_loader
    def load_user(user_id):
        from biblioteca.models import Utente  # ✅ corretto
        return db.session.get(Utente, int(user_id))

    from biblioteca.blueprints.main import main_bp
    from biblioteca.blueprints.admin import admin_bp
    from biblioteca.blueprints.auth import auth_bp
    from biblioteca.blueprints.autori import autori_bp
    from biblioteca.blueprints.opere import opere_bp
    from biblioteca.blueprints.editori import editori_bp
    from biblioteca.blueprints.dewey import dewey_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(autori_bp)
    app.register_blueprint(opere_bp)
    app.register_blueprint(editori_bp)
    app.register_blueprint(dewey_bp)

    return app