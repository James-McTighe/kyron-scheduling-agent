from flask import Flask
from api.models import db

app = Flask(__name__)  # <-- This MUST be named 'app'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scheduling.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
