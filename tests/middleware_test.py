from aecore.middleware import AECoreMiddleware
from aecore.middleware import Request
from aecore import models
from aecore.test_utils import BaseTestCase
import webapp2


__author__ = 'kyle.finley@gmail.com (Kyle Finley)'


app = AECoreMiddleware(webapp2.WSGIApplication())

class TestAECoreMiddleware(BaseTestCase):
    def setUp(self):
        super(TestAECoreMiddleware, self).setUp()
        self.register_model('User', models.User)
        self.register_model('Config', models.Config)
        self.register_model('Session', models.Session)

    def test_load_session_no_session(self):
        req = Request.blank('/auth/google')
        # No Session
        s_count = models.Session.query().count()
        self.assertEqual(s_count, 0)
        sess = req._load_session()
        s_count = models.Session.query().count()
        self.assertEqual(s_count, 1)

    def test_load_session_session_id_no_user_id(self):
        # Cookie session_id but no user_id
        s = models.Session.create()
        s_count = models.Session.query().count()
        self.assertEqual(s_count, 1)
        req = Request.blank('/auth/google')
        req.cookies[u'_aecore'] = s.serialize()
        req._load_session()
        # Assert No new session was created
        s_count2 = models.Session.query().count()
        self.assertEqual(s_count2, 1)
        self.assertEqual(req.session.session_id, s.session_id)

    def test_load_session_session_id_and_user_id(self):
        # Cookie session_id and user_id
        s = models.Session.create()
        s_count = models.Session.query().count()
        self.assertEqual(s_count, 1)
        req = Request.blank('/auth/google')
        req.cookies[u'_aecore'] = s.serialize()
        req._load_session()
        # Assert No new session was created
        s_count2 = models.Session.query().count()
        self.assertEqual(s_count2, 1)
        self.assertEqual(req.session.session_id, s.session_id)

    def test_load_session_cookie_and_no_session(self):
        # Cookie and not session
        s = models.Session.create()
        old_sid = s.session_id
        s_serialized = s.serialize()
        s.key.delete()
        s_count = models.Session.query().count()
        self.assertEqual(s_count, 0)
        req = Request.blank('/auth/google')
        req.cookies[u'_aecore'] = s_serialized
        req._load_session()
        # Assert that a new session was created
        self.assertNotEqual(req.session.session_id, old_sid)
        # Assert No new session was created
        s_count2 = models.Session.query().count()
        self.assertEqual(s_count2, 1)

    def test_save_session(self):
        # Cookie session_id but no user_id
        s = models.Session.create()
        s_count = models.Session.query().count()
        self.assertEqual(s_count, 1)

        req = Request.blank('/auth/google')
        req.cookies[u'_aecore'] = s.serialize()
        req._load_session()
        resp = req.get_response(app)
        resp.request = req
        resp._save_session()

        self.assertEqual(resp.request.session.session_id, s.session_id)
        # Assert No new session was created
        s_count2 = models.Session.query().count()
        self.assertEqual(s_count2, 1)

        # Add a user_id to session
        resp.request.session.user_id = '1'
        resp._save_session()
        # a new session should be created with the user_id as it's id
#        self.assertEqual(resp.request.session.key.id(), '1')
        s_count = models.Session.query().count()
        self.assertEqual(s_count, 1)
        s1 = models.Session.query().get()
        self.assertEqual(s1.key.id(), '1')

    def test__load_user(self):
        user = models.User.create()
        req = Request.blank('/auth/google')
        req._load_session()
        req.session.user_id = user.get_id()
        req._load_user()
        self.assertEqual(user, req.user)

    def test_add_message(self):
        req = Request.blank('/auth/google')
        req._load_session()

        msgs = req.get_messages()
        self.assertEqual(msgs, None)

        req.add_message('TEST MESSAGE')
        msgs = req.get_messages()
        self.assertEqual(msgs, [{'level': None, 'message':'TEST MESSAGE' }])

        # Get again should be none.
        msgs = req.get_messages()
        self.assertEqual(msgs, None)

        # add message with level error
        req.add_message('TEST1', 'error')
        # add another message with level error
        req.add_message('TEST2', 'success')

        msgs = req.get_messages()
        self.assertEqual(msgs, [
                {'level': 'error', 'message':'TEST1' },
                {'level': 'success', 'message':'TEST2' },
        ])
        # Get again should be none.
        msgs = req.get_messages()
        self.assertEqual(msgs, None)

        # Test with different key.
        # add message with level error
        req.add_message('TEST1', 'error')
        # add another message with level error
        req.add_message('TEST2', 'success', '_mykey')

        msgs = req.get_messages()
        self.assertEqual(msgs, [
                {'level': 'error', 'message':'TEST1' },
        ])
        msgs_key = req.get_messages('_mykey')
        self.assertEqual(msgs_key, [
                {'level': 'success', 'message':'TEST2' },
        ])
        # Get again should be none.
        msgs = req.get_messages()
        self.assertEqual(msgs, None)
        msgs_key = req.get_messages()
        self.assertEqual(msgs_key, None)

    def test_set_redirect_url(self):
        # test without next uri
        req = Request.blank('/auth/google')
        req._load_session()
        req.set_redirect_url()
        redirect_url = req.get_redirect_url()
        self.assertEqual(redirect_url, None)

        # test with out next uri
        req = Request.blank('/auth/google?next=/newcallback')
        req._load_session()
        req.set_redirect_url()
        redirect_url = req.get_redirect_url()
        self.assertEqual(redirect_url, '/newcallback')

        req = Request.blank('/auth/google?next=/newcallback&a=121&123=a')
        req._load_session()
        req.set_redirect_url()
        redirect_url = req.get_redirect_url()
        self.assertEqual(redirect_url, '/newcallback')

