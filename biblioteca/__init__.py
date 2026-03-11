from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/bibliotecaDb'
db = SQLAlchemy(app)

from biblioteca import routes
