import unittest
from app import create_app, db
from app.models import User, Role, Size, Format, Title, encode_id
from flask import url_for
import re


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app.secret_key = "testing"
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        Format.insert_formats()
        Size.insert_sizes()
        self.client = self.app.test_client(use_cookies=True)

        user_role = Role.query.filter_by(name='user').first()
        admin_role = Role.query.filter_by(name='admin').first()
        user = User(
            email='profile_john@example.com',
            username='profile_john',
            password='yolo',
            about_me="Overlord",
            location='Detroit',
            role=admin_role,
            confirmed=True)
        db.session.add(user)
        user2 = User(
            email='profile_john2@example.com',
            username='profile_john2',
            password='yolo',
            about_me="not in charge",
            location="USA",
            role=user_role,
            confirmed=True)
        db.session.add(user2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post(url_for("main.index"), data=dict(
            email=email, password=password, remember_me=True),
            follow_redirects=True)

    def logout(self):
        return self.client.get(url_for("auth.logout"), follow_redirects=True)

    def register(self, email, username, password, password2):
        return self.client.post(url_for("auth.register"), data=dict(
            email=email, password=password, username=username, password2=password), follow_redirects=True)

    def add_record(self, username, mail=None):
        return self.client.post(
            url_for("main.user", username=username),
            data=dict(
                artist="Black Sabbath",
                title="Master of Reality",
                format=1,
                color="Black",
                size=3,
                year=1970,
                notes="Lorem",
                incoming=mail),
            follow_redirects=True)

    def delete_record(self, record_id):
        hashed_id = encode_id(record_id)
        return self.client.get(
            url_for('main.delete_record', hashed_id=hashed_id), follow_redirects=True)

    def arrive_record(self, record_id):
        hashed_id = encode_id(record_id)
        return self.client.get(
            url_for('main.update_record', hashed_id=hashed_id), follow_redirects=True)

    def edit_profile(self):
        return self.client.post(
            url_for("main.edit_profile"),
            data=dict(location="yolo"), follow_redirects=True)

    def change_user_password(self, old, new, new2):
        return self.client.post(
            url_for('auth.change_password'),
            data=dict(old_password=old, password=new, password2=new2),
            follow_redirects=True)

    def password_reset_request(self, email):
        return self.client.post(
            url_for('auth.password_reset_request'),
            data=dict(email=email),
            follow_redirects=True)

    def reset_password(self, email, new_password, token):
        return self.client.post(
            url_for('auth.password_reset', token=token),
            data=dict(email=email, password=new_password, password2=new_password),
            follow_redirects=True)

    # ------ Functionality ------#

    # Login #
    def test_login_and_logout(self):
        response = self.login(email="profile_john@example.com", password="yolo")
        assert '<h4 class="media-heading">profile_john</h4>' in response.data
        assert '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/ekko-lightbox/5.2.0/ekko-lightbox.min.css">' in response.data
        response = self.logout()
        assert "You have logged out" in response.data

    def test_nonexistent_user_login(self):
        response = self.login(email="fakeuser@example.com", password="yolo")
        assert "Invalid username or password" in response.data

    def test_login_fields_required(self):
        response = self.login(email="", password="")
        assert "Email is required" in response.data
        assert "Password is required" in response.data

    def test_invalid_email_format(self):
        response = self.login(email="fakeuser", password="yolo")
        assert 'Invalid email address' in response.data

    def test_invalid_password(self):
        response = self.login(email="profile_john@example.com", password="yolo1")
        assert "Invalid username or password" in response.data

    # Add a record #
    def test_add_record(self):
        # Login
        self.login(email="profile_john@example.com", password="yolo")
        response = self.add_record(username="profile_john", mail=0)
        assert "Black Sabbath - Master of Reality Added!" in response.data

    def test_add_record_as_different_user(self):
        self.login(email="profile_john@example.com", password="yolo")
        response = self.add_record(username="kgjkhgh", mail=0)
        assert response.status_code == 404

    def test_add_mail_record(self):
        self.login(email="profile_john@example.com", password="yolo")
        response = self.add_record(username="profile_john", mail=1)
        stripped_response = re.sub(r'\s+', '', response.data)
        assert '<divid="twelve_inches_mail"class="panelpanel-default"><!--Defaultpanelcontents--><divclass="panel-heading"><strong>12Inches</strong><spanclass="badgepull-right">1</span>' in stripped_response

    # def test_arrive_record(self):
    # 	self.login(email="profile_john@example.com", password="yolo")
    # 	self.add_record(username="profile_john", mail=1)
    # 	record_id = Title.query.filter_by(mail=1).first().id
    # 	response = self.arrive_record(record_id)
    # 	stripped_response = re.sub(r'\s+', '', response.data)
    # 	assert '<divid="twelve_inches"class="panelpanel-default"><!--Defaultpanelcontents--><divclass="panel-heading"><strong>12Inches</strong><spanclass="badgepull-right">1</span></' in stripped_response

    # Delete a record #
    def test_delete_record(self):
        self.login(email="profile_john@example.com", password="yolo")
        self.add_record(username="profile_john")
        response = self.delete_record(Title.query.first().id)
        assert "Black Sabbath - Master of Reality Deleted!" in response.data

    def test_delete_nonowned_record(self):
        self.login(email="profile_john@example.com", password="yolo")
        self.add_record(username="profile_john")
        self.logout()
        self.login(email="profile_john2@example.com", password="yolo")
        response = self.delete_record(Title.query.first().id)
        assert "You dont own that" in response.data

    def test_delete_nonexistent_record(self):
        self.login(email="profile_john@example.com", password="yolo")
        self.add_record(username="profile_john")
        response = self.delete_record(99)
        assert response.status_code == 404

    # Edit Profile #
    def test_edit_profile(self):
        self.login(email="profile_john@example.com", password="yolo")
        response = self.client.get("/edit-profile")
        assert "Detroit" in response.data
        response = self.edit_profile()
        assert "yolo" in response.data

    def test_admin_edit_profile(self):
        self.login(email="profile_john@example.com", password="yolo")
        response = self.client.get("/edit-profile/1")
        assert "Detroit" in response.data
        response = self.edit_profile()
        assert "yolo" in response.data

    def test_admin_edit_other_profile(self):
        self.login(email="profile_john@example.com", password="yolo")
        response = self.client.get("/edit-profile/2")
        assert "Confirmed" in response.data
        assert "not in charge" in response.data
        response = self.edit_profile()
        assert "yolo" in response.data

    def test_user_edit_other_profile(self):
        self.login(email="profile_john2@example.com", password="yolo")
        response = self.client.get("/edit-profile/1")
        assert response.status_code == 403

    # Register #
    def test_register(self):
        response = self.client.get(url_for("auth.register"))
        assert "Register" in response.data
        response = self.register(
            email="test@example.com", username="test", password="testtest", password2="testtest")
        assert "A confirmation email has been sent to test@example.com." in response.data

        response = self.login(email="test@example.com", password="testtest")
        assert "Need another confirmation email?" in response.data

        test_user = User.query.filter_by(email="test@example.com").first()
        test_user.confirmed = True

        response = self.client.get(url_for("main.user", username="test"))
        assert '<h4 class="media-heading">test</h4>' in response.data

    def test_register_email_exists(self):
        response = self.client.get(url_for("auth.register"))
        assert "Register" in response.data
        response = self.register(
            email="profile_john@example.com", username="test", password="test", password2="test")
        assert "Email already registered." in response.data

    def test_register_username_exists(self):
        response = self.client.get(url_for("auth.register"))
        assert "Register" in response.data
        response = self.register(
            email="yolo@example.com", username="profile_john", password="test", password2="test")
        assert "Username already registered." in response.data

    def test_register_forbidden_username(self):
        response = self.client.get(url_for("auth.register"))
        assert "Register" in response.data
        response = self.register(
            email="yolo@example.com", username="register", password="test", password2="test")
        assert "Please choose a different username" in response.data

    def test_regex_username(self):
        response = self.client.get(url_for("auth.register"))
        assert "Register" in response.data
        response = self.register(
            email="yolo@example.com", username="!!!", password="test", password2="test")
        assert "Usernames can only contain letters and numbers" in response.data

    def test_register_fields_required(self):
        response = self.client.get(url_for("auth.register"))
        assert "Register" in response.data
        response = self.register(
            email="", username="", password="", password2="")
        assert "Email is required" in response.data
        assert "Username is required" in response.data
        assert "Password is required" in response.data
        assert "Password match is required" in response.data

    # Change Password
    def test_change_password(self):
        self.login(email="profile_john@example.com", password="yolo")
        response = self.client.get(url_for('auth.change_password'))
        assert "Change password" in response.data

        response = self.change_user_password(old="yolo", new="yolo1", new2="yolo1")
        assert "Your password has been updated." in response.data

    def test_change_password_bad_new(self):
        self.login(email="profile_john@example.com", password="yolo")
        response = self.client.get(url_for('auth.change_password'))
        assert "Change password" in response.data

        response = self.change_user_password(old="yolo", new="yolo1", new2="yolo3")
        assert "Passwords must match" in response.data

    def test_change_password_bad_current_pw(self):
        self.login(email="profile_john@example.com", password="yolo")
        response = self.client.get(url_for('auth.change_password'))
        assert "Change password" in response.data

        response = self.change_user_password(old="yolo7", new="yolo1", new2="yolo1")
        assert "invalid password" in response.data

    # Password Reset
    def test_password_reset_request(self):
        response = self.password_reset_request(email="profile_john@example.com")
        assert "An email with instructions has been sent to you." in response.data

        user = User.query.filter_by(email="profile_john@example.com").first()
        token = user.generate_reset_token()

        response = self.reset_password(email="profile_john@example.com", new_password="yolo", token=token)
        assert "Your password has been updated" in response.data

    def test_password_reset_nonexistent_email(self):
        response = self.password_reset_request(email="yolo@swag.com")
        assert "There is no account associated with that email address" in response.data

    def test_password_reset_request_bad_email_format(self):
        response = self.password_reset_request(email="yolo")
        assert "Invalid email address." in response.data

    def test_password_reset_request_bad_token(self):
        response = self.password_reset_request(email="profile_john@example.com")
        assert "An email with instructions has been sent to you." in response.data

        token = "bad_token"
        response = self.reset_password(email="profile_john@example.com", new_password="yolo", token=token)
        assert "Something went wrong, password not updated" in response.data

    # Status Code/CSS/Static
    def test_home_page_status(self):
        response = self.client.get(url_for('main.index'))
        assert response.status_code == 200
        stripped_response = re.sub(r'\s+', '', response.data)
        assert '<liclass="active"><ahref="/">Home</a></li>' in stripped_response
        assert '<linkrel="stylesheet"href="https://cdnjs.cloudflare.com/ajax/libs/ekko-lightbox/5.2.0/ekko-lightbox.min.css">' not in stripped_response

    def test_register_page_status(self):
        response = self.client.get(url_for('auth.register'))
        assert response.status_code == 200
        stripped_response = re.sub(r'\s+', '', response.data)
        assert '<liclass="active"><ahref="/auth/register">Register</a></li>' in stripped_response

    def test_password_reset_page_status(self):
        response = self.client.get(url_for('auth.password_reset_request'))
        assert response.status_code == 200

    def test_public_profile_page_status(self):
        response = self.client.get('/profile_john')
        assert response.status_code == 200

    def test_all_users_page_status(self):
        response = self.client.get(url_for('main.all_users'))
        stripped_response = re.sub(r'\s+', '', response.data)
        assert '<liclass="active"><ahref="/users">Users</a></li>' in stripped_response

    def test_404_status(self):
        response = self.client.get("/yolo")
        assert response.status_code == 404

    def test_unconfirmed_redirect(self):
        response = self.client.get(url_for('auth.unconfirmed'))
        assert response.status_code == 302

    def test_change_email_redirect(self):
        response = self.client.get(url_for('auth.change_email_request'))
        assert response.status_code == 302

    def test_change_password_redirect(self):
        response = self.client.get(url_for('auth.change_password'))
        assert response.status_code == 302

    def test_logout_redirect(self):
        response = self.client.get(url_for('auth.logout'))
        assert response.status_code == 302

    def test_confirm_resend_redirect(self):
        response = self.client.get(url_for('auth.resend_confirmation'))
        assert response.status_code == 302

    def test_confirm_redirect(self):
        response = self.client.get(url_for('auth.confirm', token='xyz'))
        assert response.status_code == 302

    def test_edit_profile_redirect(self):
        response = self.client.get("/edit-profile")
        assert response.status_code == 302

    def test_admin_edit_profile_redirect(self):
        response = self.client.get("/edit-profile/1")
        assert response.status_code == 302
