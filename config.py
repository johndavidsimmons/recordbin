import os

base_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY')
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	MAIL_SERVER = 'smtp.googlemail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = 'johndavidsimmons@gmail.com'
	MAIL_PASSWORD = 'dofoprdqzwfrhtty'
	FLASKY_MAIL_SUBJECT_PREFIX = '[RecordBin]'
	FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
	FLASKY_ADMIN = 'Flasky Admin <flasky@example.com>'


	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI ='sqlite:///' + os.path.join(base_dir, 'data-dev.sqlite')

class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI ='sqlite:///' + os.path.join(base_dir, 'data-test.sqlite')

class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI ='sqlite:///' + os.path.join(base_dir, 'data.sqlite')		


config = {'development' : DevelopmentConfig, 'testing':TestingConfig, 'production':ProductionConfig, 'default':DevelopmentConfig}
