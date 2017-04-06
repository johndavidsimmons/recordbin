from flask_wtf import Form
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import Required, Email, Length, Regexp, ValidationError
from ..models import Role, User, Format, Size
import datetime


class NameForm(Form):

    name = StringField('What is your name?', validators=[
        Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):

    name = StringField('Real name', validators=[
        Length(0, 64)])
    location = StringField('Location', validators=[
        Length(0, 64)])

    about_me = TextAreaField('About me')

    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):

    email = StringField('Email', validators=[
        Required(),
        Length(1, 64),
        Email()])

    username = StringField('Username', validators=[
        Required(),
        Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or underscores')])

    confirmed = BooleanField('Confirmed')

    role = SelectField('Role', coerce=int)

    name = StringField('Real name', validators=[
        Length(0, 64)])

    location = StringField('Location', validators=[
        Length(0, 64)])

    about_me = TextAreaField('About me')

    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        """Autofill dropdown menus with choices"""
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        """Test that the email address isn't already registered"""
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        """Test that the username doesn't already exist"""
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class AddRecordForm(Form):
    artist = StringField('Artist', validators=[
        Required()])

    title = StringField('Title', validators=[
        Required()])

    year = SelectField("Year", coerce=int, validators=[
        Required()])

    format = SelectField('Format', coerce=int)

    notes = TextAreaField('Notes')

    color = StringField('Color', validators=[
        Required()])

    size = SelectField('Size', coerce=int)

    incoming = BooleanField('Mail')

    def __init__(self, *args, **kwargs):
        """Auto fill dropdown menus with choices"""
        super(AddRecordForm, self).__init__(*args, **kwargs)

        # Formats
        formats = Format.query.order_by(Format.id).all()
        self.format.choices = [(format.id, format.name) for format in formats]

        # Record Sizes
        self.size.choices = [(size.id, size.name) for size in Size.query.order_by(Size.id).all()]

        # Release Years
        years = list(xrange(1950, datetime.datetime.now().year + 1))
        years.sort(reverse=True)
        self.year.choices = [(value, value) for value in years]
