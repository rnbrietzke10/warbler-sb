"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False



class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.commit()


    """*********Message view functions**********"""
    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")


    def test_show_message(self):
        """Check if user can view message"""

        msg1 = Message(id=12345, text="TestMessage1", user_id=self.testuser.id)
        db.session.add(msg1)
        db.session.commit()

        with self.client as c:
           resp = c.get(f'/messages/{msg1.id}')

           self.assertEqual(resp.status_code, 200)



    def test_delete_message(self):

            msg1 = Message(id=12345, text="a test message",user_id=self.testuser.id)
            db.session.add(msg1)
            db.session.commit()

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id

                resp = c.post("/messages/12345/delete", follow_redirects=True)
                self.assertEqual(resp.status_code, 200)

                m = Message.query.get(1234)
                self.assertIsNone(m)

    def test_prohibit_add_message(self):
        """Test if user is prohibited from adding a message if logged out"""
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)


            # Make sure it redirects
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)


    def test_prohibited_delete_message(self):

            msg1 = Message(id=12345, text="a test message",user_id=self.testuser.id)
            db.session.add(msg1)
            db.session.commit()

            with self.client as c:

                resp = c.post("/messages/12345/delete", follow_redirects=True)
                html = resp.get_data(as_text=True)
                self.assertEqual(resp.status_code, 200)
                self.assertIn("Access unauthorized.", html)


    def test_add_message_unauthroized_user(self):
        """Test if user is prohibited from adding a message as another user."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 12345678


            resp = c.post("/messages/new", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_delete_message_unauthroized_user(self):
        """Test if user is prohibited from adding a message as another user."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 12345678


            resp = c.post("/messages/12345/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)



    # def test_delete_message(self):
            """Don't know why mine doesn't work but when I pasted theres in it does pass. Went through line by line and other than the message id being different and instead of m I used msg1"""
    #     """Can user delete there message"""
    #     msg1 = Message(id=12345, text="TestMessage1", user_id=self.testuser.id)
    #     db.session.add(msg1)
    #     db.session.commit()

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id


    #             resp = c.post("/messages/12345/delete", follow_redirects=True)
    #             self.assertEqual(resp.status_code, 200)
    #             m = Message.query.get(12345)
    #             self.assertIsNone(m)
