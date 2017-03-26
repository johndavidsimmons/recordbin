import unittest
import time
from app import create_app, db
from app.models import User, AnonymousUser, Title, Size, Format, Artist, Role
from datetime import datetime

def _artist():
	return Artist(name="Black Sabbath")

def _title():
	return Title(
			name="Master of Reality", 
			artist_id=1, 
			year=1970, 
			format_id=1, 
			owner_id=1,
			mail=0, 
			size_id=3, 
			color="black", 
			notes="lorem")

class UserModelTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_add_artist_to_table(self):
		a = _artist()
		a.add_to_table()
		self.assertTrue(Artist.query.filter_by(name=a.name).first())

		b = Artist(name="Thin Lizzy")
		b.add_to_table()
		self.assertEquals(len(Artist.query.all()), 2) 		

	def test_delete_artist_from_table(self):
		a = _artist()
		a.add_to_table()
		self.assertTrue(Artist.query.filter_by(name=a.name).first())
		a.delete_from_table()
		self.assertTrue(Artist.query.filter_by(name=a.name).first() is None)

	def test_add_identical_artist_to_table(self):
		from sqlalchemy.exc import IntegrityError
		a = _artist()
		b = _artist()
		a.add_to_table()
		with self.assertRaises(IntegrityError):
			b.add_to_table()

	def test_artist_doesnt_exist(self):
		a = _artist()
		self.assertTrue(Artist.query.filter_by(name=a.name).first() is None)

	def test_format_create(self):
		a = Format(name='vinyl')
		db.session.add(a)
		db.session.commit()
		self.assertTrue(Format.query.filter_by(name=a.name).first())

	def test_format_delete(self):
		a = Format(name='vinyl')
		db.session.add(a)
		db.session.commit()
		self.assertTrue(Format.query.filter_by(name=a.name).first())
		db.session.delete(Format.query.filter_by(name=a.name).first())
		db.session.commit()
		self.assertTrue(Format.query.filter_by(name=a.name).first() is None)

	def test_create_all_formats(self):
		self.assertTrue(len(Format.query.all()) == 0) 
		Format.insert_formats()	
		self.assertTrue(len(Format.query.all()) == 1)		

	def test_size_create(self):
		a = Size(name=7)
		db.session.add(a)
		db.session.commit()
		self.assertTrue(Size.query.filter_by(name=7).first())

	def test_size_delete(self):
		a = Size(name=7)
		db.session.add(a)
		db.session.commit()
		self.assertTrue(Size.query.filter_by(name=7).first())
		db.session.delete(Size.query.filter_by(name=7).first())
		db.session.commit()
		self.assertTrue(Size.query.filter_by(name=7).first() is None)

	def create_all_sizes(self):
		self.assertTrue(len(Size.query.all()) == 0)
		Size.insert_sizes()	
		self.assertTrue(len(Size.query.all()) == 1)

	def test_title_create_method(self):
		t = _title()
		t.add_to_table()
		self.assertTrue(Title.query.filter_by(
			name=t.name, 
			artist_id=t.artist_id, 
			year=t.year, 
			format_id=t.format_id,
			mail=t.mail, 
			size_id=t.size_id, 
			color=t.color, 
			notes=t.notes, 
			owner_id=t.owner_id).first())

	def test_title_delete_method(self):
		t = _title()
		t.add_to_table()
		d = Title.query.filter_by(
			name=t.name, 
			artist_id=t.artist_id, 
			year=t.year, 
			format_id=t.format_id,
			mail=t.mail, 
			size_id=t.size_id, 
			color=t.color, 
			notes=t.notes, 
			owner_id=t.owner_id).first()
		self.assertTrue(d)
		d.delete_from_table()
		self.assertTrue(len(Title.query.all()) == 0)

	def test_title_timestamp(self):
		import datetime
		t = _title()
		t.add_to_table()
		self.assertTrue((t.timestamp.year, t.timestamp.month, t.timestamp.day) == (datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day))
			