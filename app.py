from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_script import Manager
from flask_script import Shell
from flask.ext.migrate import Migrate, MigrateCommand
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

import os

from models import NameForm



app = Flask(__name__)

manager = Manager(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


def make_shell_context():
	return dict(app=app, db=db, User=User, Role=Role)

manager.add_command('shell', Shell(make_context = make_shell_context))
manager.add_command('db', MigrateCommand)	





@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
    	user = User.query.filter_by(username=form.name.data).first()
    	if user is None:
    		user = User(username=form.name.data)
    		db.session.add(user)
    		session['known'] = False
    	else:
    		session['known'] = True
    	session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', form=form, 
    	name=session.get('name'), known=session.get('known', False))


if __name__ == '__main__':
    manager.run()
