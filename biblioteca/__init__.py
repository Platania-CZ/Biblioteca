from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/bibliotecaDb'
app.config['SECRET_KEY'] = '2227a0349dc08ade8b5f501a52c8c7d3'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from biblioteca import routes

from flask_login import LoginManager

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from biblioteca.models import Utente
    return Utente.query.get(int(user_id))