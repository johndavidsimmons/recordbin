import factory

from app import db
from app.models import Role, User


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    email = factory.Sequence(lambda n: 'user{}@example.com'.format(n))
    username = factory.Sequence(lambda n: 'user{}'.format(n))
    password = 'abc123'
    about_me = 'hello'
    location = 'world'
    confirmed = True
    role = None
    role_id = None
