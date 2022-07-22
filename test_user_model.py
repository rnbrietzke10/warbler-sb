"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy import exc

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.test_user1 = User.signup(username="testUser1", email="test1@test.com", password="1234", image_url=None)
        self.test_user1.id = 1

        self.test_user2 = User.signup(username="testUser2", email="test2@test.com", password="1234", image_url=None)
        self.test_user2.id = 2
        self.test_user3 = User.signup(username="testUser3", email="test3@test.com", password="1234", image_url=None)
        self.test_user3.id = 3

        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user__repr__method(self):
        """Test if __repr__ mehode returns the correct User instance format"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        result = u.__repr__()
        self.assertIn(f'<User #{u.id}: {u.username}, {u.email}>', result)

    def test_user_follows(self):

         follow = Follows(user_being_followed_id=self.test_user1.id, user_following_id=self.test_user2.id)
         db.session.add(follow)
         db.session.commit()

         self.assertEqual(len(self.test_user1.following), 0)
         self.assertEqual(len(self.test_user2.following), 1)
         self.assertEqual(len(self.test_user1.followers), 1)
         self.assertEqual(len(self.test_user2.followers), 0)

    def test_is_following_method(self):

         follow = Follows(user_being_followed_id=self.test_user1.id, user_following_id=self.test_user2.id)
         db.session.add(follow)
         db.session.commit()

         following = self.test_user2.is_following(self.test_user1)
         not_following = self.test_user1.is_following(self.test_user2)
         self.assertTrue(following)
         self.assertFalse(not_following)

    def test_is_followed_by_method(self):

         follow = Follows(user_being_followed_id=self.test_user1.id, user_following_id=self.test_user2.id)
         db.session.add(follow)
         db.session.commit()

         followed = self.test_user2.is_following(self.test_user1)
         not_followed = self.test_user1.is_following(self.test_user2)
         self.assertTrue(followed)
         self.assertFalse(not_followed)

    def test_user_sign_up_method(self):
        user1 = User.signup(username="user1", email="user1@gmail.com", password="123456", image_url=None)
        user_id = 300
        user1.id = user_id
        db.session.commit()

        self.assertIsInstance(user1, User)
        user1 = User.query.get(user_id)
        self.assertIsNotNone(user1)
        self.assertEqual(user1.username, "user1")
        self.assertEqual(user1.email, "user1@gmail.com")
        self.assertNotEqual(user1.password, "123456")

    def test_invalid_username_sign_up_method(self):
        """Test if invalid username is passed to signup that it throws an error."""
        user1 = User.signup(username=None, email="user1@gmail.com", password="123456", image_url=None)
        user_id = 300
        user1.id = user_id
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_invalid_email_sign_up_method(self):
        """Test if invalid username is passed to signup that it throws an error."""
        user1 = User.signup(username="test123", email=None, password="123456", image_url=None)
        user_id = 300
        user1.id = user_id
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_invalid_password_sign_up_method(self):
        """Test if invalid password is passed to signup that it throws an error."""
        with self.assertRaises(ValueError):
            User.signup(username="test123", email="user1@gmail.com", password=None, image_url=None)

    def test_valid_authentication(self):
        authenticated_user = User.authenticate(self.test_user1.username, "1234")

        self.assertIsInstance(authenticated_user, User)
        self.assertEqual(authenticated_user.id, self.test_user1.id)

    def test_invalid_username_authentication(self):
        authenticated_user = User.authenticate("random_user", "1234")

        self.assertNotIsInstance(authenticated_user, User)
        self.assertFalse(authenticated_user)

    def test_invalid_password_authentication(self):
        authenticated_user = User.authenticate(self.test_user1.username, "wrong_password")

        self.assertNotIsInstance(authenticated_user, User)
        self.assertFalse(authenticated_user)