"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes
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


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        Likes.query.delete()

        self.test_user1 = User.signup(username="testUser1", email="test1@test.com", password="1234", image_url=None)
        self.test_user1.id = 1


        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()

    def test_message_model(self):
        msg = Message(text="Test Message", user_id=self.test_user1.id)
        msg_id = 1
        msg.id =msg_id

        db.session.add(msg)
        db.session.commit()

        self.assertIsInstance(msg, Message)
        msg1 = Message.query.get(msg_id)
        self.assertEqual(msg1.user_id, self.test_user1.id)


    def test_like_messages(self):
        msg = Message(text="Test Message", user_id=self.test_user1.id)
        msg_id = 1
        msg.id =msg_id

        db.session.add(msg)
        db.session.commit()

        self.test_user1.likes.append(msg)

        db.session.commit()
        liked_msg = Message.query.get(msg_id)

        self.assertEqual(liked_msg.user_id, self.test_user1.id)
        self.assertEqual(len(self.test_user1.likes), 1)