"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py

import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"



from app import app, CURR_USER_KEY


db.create_all()


app.config['WTF_CSRF_ENABLED'] = False



class UserViewTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        """Create User and message data"""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.test_user1 = User.signup(username="testUser1", email="test1@test.com", password="1234", image_url=None)
        self.test_user1.id = 1

        self.test_user2 = User.signup(username="testUser2", email="test2@test.com", password="1234", image_url=None)
        self.test_user2.id = 2
        self.test_user3 = User.signup(username="testUser3", email="test3@test.com", password="1234", image_url=None)
        self.test_user3.id = 3

        db.session.commit()

    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()

    def test_see_following_page(self):
        """See if user is logged in they can see who they are following and who is following them"""
        new_follow = Follows(user_being_followed_id=2, user_following_id=1)
        db.session.add(new_follow)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user1.id

            resp = c.get(f'/users/{self.test_user1.id}/following')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # self.assertIn("@testUser2", html)

    def test_users_page(self):
        with self.client as c:
            resp = c.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testUser1", html)
            self.assertIn("@testUser2", html)
            self.assertIn("@testUser3", html)


    def test_user_profile(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user1.id

            resp = c.get('/users/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@testUser1', html)



    def test_anonymous_user_can_see_following_page(self):
            """See if user that is not logged is redirected to the home anon page when they try to view the following page"""
            new_follow = Follows(user_being_followed_id=2, user_following_id=1)
            db.session.add(new_follow)
            db.session.commit()

            with self.client as c:

                resp = c.get(f'/users/{self.test_user1.id}/following', follow_redirects=True)
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("New to Warbler?", html)


    """Test Followers page for logged in users and anonymous users."""
    def test_see_followers_page(self):
        """Test if the loggged in user can view the people that are following them"""
        new_follow = Follows(user_being_followed_id=2, user_following_id=1)
        db.session.add(new_follow)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user2.id

            resp = c.get(f'/users/{self.test_user2.id}/followers')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testUser", html)

    def test_anonymous_user_can_see_followers_page(self):
        """Test if the anonymous user is redirected to the home page when the try to view followers page"""
        new_follow = Follows(user_being_followed_id=2, user_following_id=1)
        db.session.add(new_follow)
        db.session.commit()

        with self.client as c:

            resp = c.get(f'/users/{self.test_user2.id}/followers', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Sign up now", html)