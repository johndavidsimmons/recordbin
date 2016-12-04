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
		self.assertTrue(len(Artist.query.all()) == 2 )	

	def test_artist_delete_manual(self):
		a = Artist(name="Black Sabbath")
		a.add_to_table()
		self.assertTrue(Artist.query.filter_by(name="Black Sabbath").first())
		db.session.delete(a)
		db.session.commit()
		self.assertTrue(Artist.query.all() == [])
		
	def test_artist_delete_method(self):
		a = Artist(name="Black Sabbath")
		a.add_to_table()
		self.assertTrue(Artist.query.filter_by(name="Black Sabbath").first())
		Artist.query.filter_by(name="Black Sabbath").first().delete_from_table()
		self.assertTrue(Artist.query.all() == [])


	def test_add_identical_artists(self):
		from sqlalchemy.exc import IntegrityError
		a = Artist(name="Black Sabbath")
		b = Artist(name="Black Sabbath")
		a.add_to_table()
		with self.assertRaises(IntegrityError):
			b.add_to_table()

	def test_artist_doesnt_exist(self):
		a = Artist(name="Black Sabbath")
		self.assertTrue(Artist.query.filter_by(name="Black Sabbath").first()==None)

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
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owners=[], size_id=3, color="black", notes="lorem")
		db.session.add(t)
		db.session.commit()
		self.assertTrue(Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem").first())

	def test_title_create_method(self):
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owners=[], size_id=3, color="black", notes="lorem")
		t.add_to_table()
		self.assertTrue(Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem").first())

	def test_title_delete_manual(self):
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owners=[], size_id=3, color="black", notes="lorem")
		t.add_to_table()
		self.assertTrue(Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem").first())
		d = Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem").first()
		db.session.delete(d)
		db.session.commit()
		self.assertTrue(Title.query.all() == [])

	def test_title_delete_method(self):
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owners=[], size_id=3, color="black", notes="lorem")
		t.add_to_table()
		self.assertTrue(Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem").first())
		d = Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem").first()
		d.delete_from_table()
		self.assertTrue(Title.query.all() == [])

	def test_title_init_owner(self):
		"""
		when a title is created it has no owners
		and the owners is an empty list
		"""

		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owners=[], size_id=3, color="black", notes="lorem")
		t.add_to_table()
		self.assertTrue(Title.query.all()[0].owners == [])

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
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owners=[], size_id=3, color="black", notes="lorem")
		t.add_to_table()
		title = Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem").first()
		self.assertTrue(title)

		# Ownership
		title.add_owner(user)		
		self.assertTrue(user in title.owners)
		self.assertTrue(title in user.titles)


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
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owners=[], size_id=3, color="black", notes="lorem")
		t.add_to_table()
		title = Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem").first()
		self.assertTrue(title)

		# Ownership
		title.add_owner(user)
		title.add_owner(user2)
		title.add_owner(user3)
		self.assertTrue(user in title.owners)
		self.assertTrue(user2 in title.owners)
		self.assertTrue(user3 in title.owners)
		self.assertTrue(title in user.titles)
		self.assertTrue(title in user2.titles)
		self.assertTrue(title in user3.titles)
		self.assertTrue(len(title.owners)==3)
		self.assertTrue(len(Title.query.all()) == 1)

	def test_ownership_delete_title(self):
		"""
		When a title is deleted it is removed from
		owner.titles
		"""

		# Create user
		u = User(email='john@example.com', password='cat')
		db.session.add(u)
		db.session.commit()
		user = User.query.filter_by(email='john@example.com').first()
		self.assertTrue(user)						
		
		# Create title
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owners=[], size_id=3, color="black", notes="lorem")
		t.add_to_table()
		title = Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem").first()
		self.assertTrue(title)

		# Ownership
		title.add_owner(user)
		self.assertTrue(user in title.owners)
		self.assertTrue(title in user.titles)

		# Delete
		title.delete_from_table()
		self.assertTrue(title not in user.titles)

	def test_multi_ownership_delete_title(self):
		"""
		when a title is deleted it is removed from all owners
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
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owners=[], size_id=3, color="black", notes="lorem")
		t.add_to_table()
		title = Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem").first()
		self.assertTrue(title)

		# Ownership
		title.add_owner(user)
		title.add_owner(user2)
		title.add_owner(user3)
		self.assertTrue(user in title.owners)
		self.assertTrue(user2 in title.owners)
		self.assertTrue(user3 in title.owners)
		self.assertTrue(title in user.titles)
		self.assertTrue(title in user2.titles)
		self.assertTrue(title in user3.titles)
		self.assertTrue(len(title.owners)==3)
		self.assertTrue(len(Title.query.all()) == 1)

		# Delete
		title.delete_from_table()
		self.assertTrue(title not in user.titles)
		self.assertTrue(title not in user2.titles)
		self.assertTrue(title not in user3.titles)

	def test_remove_owner(self):
		"""
		remove singular owner, but title still exists
		"""	

		# Create user
		u = User(email='john@example.com', password='cat')
		db.session.add(u)
		db.session.commit()
		user = User.query.filter_by(email='john@example.com').first()
		self.assertTrue(user)						
		
		# Create title
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owners=[], size_id=3, color="black", notes="lorem")
		t.add_to_table()
		title = Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem").first()
		self.assertTrue(title)

		# Ownership
		title.add_owner(user)
		self.assertTrue(user in title.owners)
		self.assertTrue(title in user.titles)

		# Remove
		title.remove_owner(user)
		self.assertTrue(user not in title.owners)
		self.assertTrue(title not in user.titles)
		self.assertTrue(len(title.owners)  == 0)
		self.assertTrue(len(user.titles) == 0)
		self.assertTrue(title)

	def test_remove_owners(self):
		"""
		remove ownership from multiple owners
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
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owners=[], size_id=3, color="black", notes="lorem")
		t.add_to_table()
		title = Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem").first()
		self.assertTrue(title)

		# Ownership
		title.add_owner(user)
		title.add_owner(user2)
		title.add_owner(user3)
		self.assertTrue(user in title.owners)
		self.assertTrue(user2 in title.owners)
		self.assertTrue(user3 in title.owners)
		self.assertTrue(title in user.titles)
		self.assertTrue(title in user2.titles)
		self.assertTrue(title in user3.titles)
		self.assertTrue(len(title.owners)==3)
		self.assertTrue(len(Title.query.all()) == 1)

		# Remove ownership
		title.remove_owner(user)
		title.remove_owner(user2)
		title.remove_owner(user3)
		self.assertTrue(user not in title.owners)
		self.assertTrue(user2 not in title.owners)
		self.assertTrue(user3 not in title.owners)
		self.assertTrue(title not in user.titles)
		self.assertTrue(title not in user2.titles)
		self.assertTrue(title not in user3.titles)
		self.assertTrue(len(title.owners)==0)
		self.assertTrue(len(Title.query.all()) == 1)

	def test_add_same_owner(self):
		"""
		title cannot have same owner in owners
		"""	

		# Create user
		u = User(email='john@example.com', password='cat')
		db.session.add(u)
		db.session.commit()
		user = User.query.filter_by(email='john@example.com').first()
		self.assertTrue(user)						
		
		# Create title
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owners=[], size_id=3, color="black", notes="lorem")
		t.add_to_table()
		title = Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem").first()
		self.assertTrue(title)

		# Ownership
		title.add_owner(user)
		title.add_owner(user)
		self.assertTrue(len(title.owners)==1)
		self.assertTrue(user in title.owners)
		self.assertTrue(title in user.titles)

	def test_add_nonuser_owner(self):
		"""
		Added user must be of user model
		"""		
		user = None

		# Create title
		t = Title(name="Master of Reality", artist_id=1, year=1970, format_id=1, owners=[], size_id=3, color="black", notes="lorem")
		t.add_to_table()
		title = Title.query.filter_by(name="Master of Reality", artist_id=1, year=1970, format_id=1, size_id=3, color="black", notes="lorem").first()
		self.assertTrue(title)

		# Ownership
		title.add_owner(user)
		self.assertTrue(len(title.owners)==0)
		with self.assertRaises(AttributeError):
			title not in user.titles		
			