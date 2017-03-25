import unittest
import time
from app import create_app, db
from app.models import User, AnonymousUser, Title, Size, Format, Artist, Role
from datetime import datetime

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

	def test_artist_creation_manual(self):
		a = Artist(name="Black Sabbath")
		db.session.add(a)
		db.session.commit()
		self.assertTrue(Artist.query.filter_by(name="Black Sabbath").first())

	def test_artist_creation_method(self):
		a = Artist(name="Thin Lizzy")
		a.add_to_table()
		self.assertTrue(Artist.query.filter_by(name="Thin Lizzy").first())

	def test_add_multiple_artists(self):
		a = Artist(name="Black Sabbath")
		b = Artist(name='Thin Lizzy')
		db.session.add(a)
		db.session.add(b)
		db.session.commit()
		self.assertEquals(len(Artist.query.all()), 2) 	

	def test_artist_delete_manual(self):
		a = Artist(name="Black Sabbath")
		a.add_to_table()
		self.assertTrue(Artist.query.filter_by(name="Black Sabbath").first())
		db.session.delete(a)
		db.session.commit()
		self.assertEquals(Artist.query.all(), [])
		
	def test_artist_delete_method(self):
		a = Artist(name="Black Sabbath")
		a.add_to_table()
		self.assertTrue(Artist.query.filter_by(name="Black Sabbath").first())
		Artist.query.filter_by(name="Black Sabbath").first().delete_from_table()
		self.assertEquals(Artist.query.all(), [])


	def test_add_identical_artists(self):
		from sqlalchemy.exc import IntegrityError
		a = Artist(name="Black Sabbath")
		b = Artist(name="Black Sabbath")
		a.add_to_table()
		with self.assertRaises(IntegrityError):
			b.add_to_table()

	def test_artist_doesnt_exist(self):
		a = Artist(name="Black Sabbath")
		self.assertEquals(Artist.query.filter_by(name="Black Sabbath").first(),None)

	def test_format_create(self):
		a = Format(name='vinyl')
		db.session.add(a)
		db.session.commit()
		self.assertTrue(Format.query.filter_by(name="vinyl").first())

	def test_format_delete(self):
		a = Format(name='vinyl')
		db.session.add(a)
		db.session.commit()
		self.assertTrue(Format.query.filter_by(name="vinyl").first())
		db.session.delete(Format.query.filter_by(name="vinyl").first())
		db.session.commit()
		self.assertTrue(Format.query.filter_by(name="vinyl").first() == None)		
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
		self.assertTrue(Size.query.filter_by(name=7).first() == None)

	def test_title_create_manual(self):
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owner_id=1, size_id=3, color="black", notes="lorem")
		db.session.add(t)
		db.session.commit()
		self.assertTrue(Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem", owner_id=1).first())

	def test_title_create_method(self):
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owner_id=1, size_id=3, color="black", notes="lorem")
		t.add_to_table()
		self.assertTrue(Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem", owner_id=1).first())

	def test_title_delete_manual(self):
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owner_id=1, size_id=3, color="black", notes="lorem")
		t.add_to_table()
		self.assertTrue(Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem", owner_id=1).first())
		d = Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem", owner_id=1).first()
		db.session.delete(d)
		db.session.commit()
		self.assertTrue(Title.query.all() == [])

	def test_title_delete_method(self):
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owner_id=1, size_id=3, color="black", notes="lorem")
		t.add_to_table()
		self.assertTrue(Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem", owner_id=1).first())
		d = Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem", owner_id=1).first()
		d.delete_from_table()
		self.assertTrue(Title.query.all() == [])

	def test_title_add_one_owner(self):
		"""
		Add a user to a title
		"""

		# Create user
		u = User(email='john@example.com', password='cat')
		db.session.add(u)
		db.session.commit()
		user = User.query.filter_by(email='john@example.com').first()
		self.assertTrue(user)						
		
		# Create title
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owner_id=u.id, size_id=3, color="black", notes="lorem")
		t.add_to_table()
		title = Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem", owner_id=u.id).first()
		self.assertTrue(title)


	def test_title_add_multi_owners(self):
		"""
		Add a multiple owners to a title
		"""

		# Create user
		u = User(email='john@example.com', password='cat')
		u2 = User(email='dave@example.com', password='cat')
		u3 = User(email='jim@example.com', password='cat')
		db.session.add(u)
		db.session.add(u2)
		db.session.add(u3)
		db.session.commit()
		user = User.query.filter_by(email='john@example.com').first()
		user2 = User.query.filter_by(email='dave@example.com').first()
		user3 = User.query.filter_by(email='jim@example.com').first()
		self.assertTrue(user)
		self.assertTrue(user2)
		self.assertTrue(user3)						
		
		# Create title
		for i in range(3):
			t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owner_id = i, size_id=3, color="black", notes="lorem")
			t.add_to_table()
			title = Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem", owner_id=i).first()
			self.assertTrue(title)
				
			