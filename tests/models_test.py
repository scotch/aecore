import datetime
from aecore.test_utils import BaseTestCase
from aecore import models
from google.appengine.ext import ndb
from aecore import types


__author__ = 'kyle.finley@gmail.com (Kyle Finley)'


class TestConfig(BaseTestCase):
    def setUp(self):
        super(TestConfig, self).setUp()
        self.register_model('Config', models.Config)

    def test_load_root_config(self):
        ac1 = models.Config.load_route_config()
        self.assertEqual(ac1['installed_apps'], ['aecore', 'aeauth', 'aerest'])

    def test_load_app_config(self):
        ac1 = models.Config.load_app_config('aecore')
        self.assertEqual(ac1['aecore']['secret_key'], 'CHANGE_TO_A_SECRET_KEY')
        self.assertEqual(ac1['aecore']['user_model'], 'aecore.models.User')

    def test_load_config_files(self):
        ac1 = models.Config.load_config_files()
        self.assertEqual(ac1['installed_apps'], ['aecore', 'aeauth', 'aerest'])
        self.assertEqual(ac1['aecore']['secret_key'], 'UPDATED')
        self.assertEqual(ac1['aecore']['user_model'], 'new.path.User')

    def test_load(self):
        ac1 = models.Config.get('aecore')
        self.assertEqual(ac1.secret_key, 'UPDATED')
        self.assertEqual(ac1.user_model, 'new.path.User')

        # Test changing values in datastore
        ac1.secret_key = 'CHANGED AGAIN'
#        ac1.put()
#
#        ac2 = models.Config.get('aecore')
#        self.assertEqual(ac2.secret_key, 'CHANGED AGAIN')


class TestUserProfile(BaseTestCase):
    def setUp(self):
        super(TestUserProfile, self).setUp()
        self.register_model('UserProfile', models.UserProfile)

    def testPersonCreate(self):

        class Person(ndb.Expando):
            name = ndb.StringProperty()

        Person.father = ndb.StructuredProperty(types.Person)
        Person._fix_up_properties()

        class UserProfile(ndb.Expando):
            person = ndb.LocalStructuredProperty(types.Person)

        user_profile = UserProfile()
        user_profile.person = types.Person(name='Full Name')
        user_profile.put()

        retrieved_profile = UserProfile.get_by_id(user_profile.key.id())

        self.assertTrue(retrieved_profile is not None)

class TestUserToken(BaseTestCase):

    def setUp(self):
        super(TestUserToken, self).setUp()
        self.register_model('UserToken', models.UserToken)

    def test_create(self):
        m = models.UserToken
        t = m.create(1, "password_reset")

        self.assertTrue(t is not None)

        s = t.key.id().split(".")
        self.assertEqual(len(s), 3)
        self.assertEqual(int(s[0]), 1)
        self.assertEqual(s[1], "password_reset")
        self.assertTrue(s[2] is not None)

        self.assertEqual(t.user_id, 1)
        self.assertEqual(t.subject, "password_reset")
        self.assertTrue(t.token is not None)


class TestUser(BaseTestCase):

    def setUp(self):
        super(TestUser, self).setUp()
        self.register_model('User', models.User)
        self.auth_id1 = models.UserProfile.generate_auth_id('test', 1)
        self.auth_id2 = models.UserProfile.generate_auth_id('test', 2)

    def test_create(self):
        m = models.User
        user = m.create(auth_id=self.auth_id1)
        self.assertTrue(user is not None)

        try:
            m.create(auth_id=self.auth_id1)
        except models.DuplicatePropertyError, e:
            self.assertEquals(e.values, [self.auth_id1])

    def test_get(self):
        m = models.User
        user = m.create(auth_id=self.auth_id1)
        self.assertTrue(user is not None)
        self.assertEqual(m.get_by_auth_id(self.auth_id1), user)
        self.assertEqual(m.get_by_auth_id(self.auth_id2), None)

    def test_add_auth_ids(self):
        m = models.User
        user = m.create(auth_id=self.auth_id1)
        user.add_auth_id(self.auth_id2)
        self.assertEqual(user.auth_ids, [self.auth_id1, self.auth_id2])
        self.assertTrue(len(user.auth_ids), 2)

        # Adding it again should have no effect
        user.add_auth_id(self.auth_id2)
        self.assertTrue(len(user.auth_ids), 2)

        # Duplicate: New user trying to add an existing users auth_id
        user2 = m.create()
        try:
            user2.add_auth_id(self.auth_id2)
        except models.DuplicatePropertyError, e:
            self.assertEquals(e.values, [self.auth_id2])

    def test_add_rolls(self):
        m = models.User
        user = m.create(auth_id=self.auth_id1)
        user.add_roll('admin')
        self.assertEqual(user.roles, ['admin'])
        self.assertTrue(len(user.roles), 1)

        # Adding it again should have no effect
        user.add_roll('admin')
        self.assertTrue(len(user.roles), 1)

        # Adding another roll
        user.add_roll('moderator')
        self.assertTrue(len(user.roles), 1)
        self.assertEqual(user.roles, ['admin', 'moderator'])

        user.put()
        # test save
        user_from_ds = user.key.get()
        self.assertEqual(user_from_ds.roles, ['admin', 'moderator'])

    def test_get_auth_id(self):
        m = models.User
        user = m.create(auth_id=self.auth_id1)

        # we should find "test"
        p = user.get_auth_id("test")
        self.assertEqual(p, self.auth_id1)

        # we should not find "fake"
        p = user.get_auth_id("fake")
        self.assertEqual(p, None)

    def test_get_profiles(self):
        m = models.User
        user = m.create(auth_id=self.auth_id1)

        # we should find "test"
        p = user.get_auth_id("test")
        self.assertEqual(p, self.auth_id1)

        # we should not find "fake"
        p = user.get_auth_id("fake")
        self.assertEqual(p, None)


class TestSession(BaseTestCase):

    def setUp(self):
        super(TestSession, self).setUp()
        self.register_model('Session', models.Session)
        self.register_model('Config', models.Config)

    def test_session_hash(self):
        # Change user_id
        s1 = models.Session.create()
        h1 = s1.hash()
        s1.user_id = '1'
        h2 = s1.hash()
        self.assertNotEqual(h1, h2)

        # Change sid
        s1 = models.Session.create()
        h1 = s1.hash()
        s1.session_id = '1'
        h2 = s1.hash()
        self.assertNotEqual(h1, h2)

        # Add data
        s1 = models.Session.create()
        h1 = s1.hash()
        s1.data['a'] = '1'
        h2 = s1.hash()
        self.assertNotEqual(h1, h2)

        # Change data
        s1 = models.Session.create()
        s1.data['a'] = '1'
        h1 = s1.hash()
        s1.data['a'] = '2'
        h2 = s1.hash()
        self.assertNotEqual(h1, h2)

        # Change data back
        s1 = models.Session.create()
        s1.data['a'] = '1'
        h1 = s1.hash()
        s1.data['a'] = '2'
        h2 = s1.hash()
        s1.data['a'] = '1'
        h3 = s1.hash()
        self.assertEqual(h1, h3)

        # complex data
        s1 = models.Session.create()
        s1.data['a'] = {1:'a', 2:{'a': '1', 'b': {2:None}}}
        h1 = s1.hash()
        s1.data['a'] = {1:'a', 2:{'a': '1', 'b': {2:True}}}
        h2 = s1.hash()
        s1.data['a'] = {1:'a', 2:{'a': '1', 'b': {2:None}}}
        h3 = s1.hash()
        self.assertNotEqual(h1, h2)
        self.assertEqual(h1, h3)

        # ignore data order
        s1 = models.Session.create()
        s1.data['a'] = {1:'a', 2:'b'}
        h1 = s1.hash()
        s1.data['a'] = {2:'b', 1:'a'}
        h2 = s1.hash()
        self.assertEqual(h1, h2)

    def test_create(self):
        s1 = models.Session.create()
        self.assertIsNotNone(s1.key.id())
        user_id = 1
        data = {'a': 1, 2: 'bee', 3: {4: True, 5: 'false'}}
        # Test Create with user_id
        s2 = models.Session.create(user_id=user_id)
        s2_from_db = models.Session.get_by_id(s2.key.id())
        self.assertEqual(s2, s2_from_db)
        self.assertEqual(s2_from_db.data, {})
        s2_from_db.data['test_key'] = 'test_value'
        self.assertDictEqual(s2_from_db.data, {'test_key': 'test_value'})
        # Test Create with user_id and data
        s3 = models.Session.create(user_id=user_id, data=data)
        s3_from_db = models.Session.get_by_id(s3.key.id())
        self.assertEqual(s3, s3_from_db)
        self.assertEqual(s3_from_db.data, data)

    def test_get_by_sid(self):
        s1 = models.Session.create()
        sid = s1.session_id
        s = models.Session.get_by_sid(sid)
        self.assertEqual(s, s1)

    def test_get_user_id(self):
        user_id = 1
        s2 = models.Session.create(user_id=user_id)
        s2_db = models.Session.get_by_user_id(user_id)
        self.assertEqual(s2, s2_db)

    def test_serializer(self):
        s1 = models.Session.create()
        raw_values = s1.to_dict(include=['session_id', 'user_id'])
        data_serialized = s1.serialize()
        data_deserialize = models.Session.deserialize(data_serialized)
        self.assertEqual(raw_values, data_deserialize)

    def test_get_by_value(self):
        s1 = models.Session.create()
        data_serialized = s1.serialize()
        s1_from_value = models.Session.get_by_value(data_serialized)
        self.assertEqual(s1, s1_from_value)

    def test_upgrade_to_user_session(self):
        s1 = models.Session.create()
        test_data = {'a':1, 'b': 2, 3:{'c':'d', 'e': 'f'}}
        s1.data = test_data
        s1.put()
        s_count1 = models.Session.query().count()
        self.assertEqual(s_count1, 1)

        user_id = '1'
        s2 = models.Session.upgrade_to_user_session(s1.session_id, user_id)
        self.assertEqual(s2.session_id, user_id)
        self.assertEqual(s2.user_id, user_id)

        self.assertEqual(s2.data, test_data)

        s_count2 = models.Session.query().count()
        self.assertEqual(s_count2, 1)

        sq = models.Session.query().get()
        self.assertEqual(s2.user_id, sq.user_id)
        self.assertEqual(s2.session_id, sq.session_id)

    def test_delete_inactive(self):
        def add_sessions(count=10, days_old=30):
            for i in range(0, count):
                days_ago = days_old + i
                id = str(i)
                s = models.Session(id=id, session_id=id)
                s.updated = datetime.datetime.now() + datetime.timedelta(-days_ago)
                s.put()

        add_sessions()
        now_offset = datetime.datetime.now() + datetime.timedelta(31)
        s_count1 = models.Session.query().count()
        self.assertEqual(s_count1, 10)
        models.Session.remove_inactive(now=now_offset)
        s_count2 = models.Session.query().count()
        self.assertEqual(s_count2, 0)

        add_sessions()
        s_count1 = models.Session.query().count()
        self.assertEqual(s_count1, 10)
        models.Session.remove_inactive(35, now=now_offset)
        s_count2 = models.Session.query().count()
        self.assertEqual(s_count2, 10)


