#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Follow, Role, Title, Artist, Permission, Size, Format, user_local_time, Image
from flask_script import Manager
from flask_script import Shell
from flask.ext.migrate import Migrate, MigrateCommand
from flask_sslify import SSLify

COV = None

if os.environ.get('FLASK_COVERAGE'):
	import coverage
	COV = coverage.coverage(branch=True, include='app/*')
	COV.start()

if os.path.exists('.env'):
	print('Importing environment from .env...')
	for line in open('.env'):
		var = line.strip().split('=')
		if len(var) == 2:
			os.environ[var[0]] = var[1]

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
# sslify = SSLify(app, permanent=True)


def make_shell_context():
	return dict(
		app=app, db=db, User=User,
		Role=Role, Artist=Artist, Title=Title,
		Permission=Permission, Follow=Follow, Size=Size,
		Format=Format, user_local_time=user_local_time, Image=Image)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
	"""Run the unit tests."""
	if coverage and not os.environ.get('FLASK_COVERAGE'):
		import sys
		os.environ['FLASK_COVERAGE'] = '1'
		os.execvp(sys.executable, [sys.executable] + sys.argv)

	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)

	if COV:
		COV.stop()
		COV.save()
		print "Coverage Summary"
		COV.report()
		basedir = os.path.abspath(os.path.dirname(__file__))
		covdir = os.path.join(basedir, 'tmp/coverage')
		COV.html_report(directory=covdir)
		print 'HTML version: file://{}/index.html'.format(covdir)
		COV.erase()


@manager.command
def deploy():
	"""Run Deployment tasks"""
	from flask_migrate import upgrade
	from app.models import Role, User, Size, Format

	# migrate database to latest revision
	upgrade()

	# create user roles
	Role.insert_roles()

	# create self-follows for all users
	User.add_self_follows()

	Format.insert_formats()

	Size.insert_sizes()

	db.session.commit()

if __name__ == '__main__':
	manager.run()
