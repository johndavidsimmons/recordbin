from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_script import Manager
from flask_login import LoginManager
from flask_mail import Mail
from flask.ext.scss import Scss

manager = Manager()
moment = Moment()
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
login_manager.session_protection = 'basic'
login_manager.login_view = 'main.index'

def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	moment.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)
	Scss(app, static_dir='app/static/css', asset_dir='app/static/assets')

	from main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint, url_prefix='/auth')

	return app