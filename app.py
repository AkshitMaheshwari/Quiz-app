from flask import Flask, redirect, url_for
from flask_login import LoginManager
from models.models import db, User
from controllers.auth import auth, login_manager
import os
from flask_migrate import Migrate
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('Secret_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
migrate = Migrate(app, db)

app.register_blueprint(auth)
from controllers.admin import admin  
app.register_blueprint(admin, url_prefix='/admin')
from controllers.main import main
app.register_blueprint(main, url_prefix='/main')

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)
