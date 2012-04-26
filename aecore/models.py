# -*- coding: utf-8 -*-
"""
    aecore.models
    ====================================

    :copyright: 2012 by Kyle Finley.
    :license: Apache Software License, see LICENSE for details.

    :copyright: 2011 by Rodrigo Moraes.
    :license: Apache Software License, see LICENSE for details.

    :copyright: 2011 by tipfy.org.
    :license: Apache Software License, see LICENSE for details.

"""
import itertools
from aecore import types
from aecore.utils import dotdict
import datetime
from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from webapp2_extras import security
from webapp2_extras import securecookie

__all__ = [
    'Config',
    'Session',
    'User',
    'Webapp2User'
#    'UserEmail',
    'UserProfile',
    'UserToken',
    ]

class AECoreError(Exception):
    """Base user exception."""

class DuplicatePropertyError(AECoreError):
    def __init__(self, value):
        self.values = value
        self.msg = u'duplicate properties(s) were found.'


class Config(ndb.Model):

    data = ndb.JsonProperty('d')

    @staticmethod
    def _load_route_config():
        try:
            import appengine_config
            import os
            import yaml

            root_dir = os.path.dirname(appengine_config.__file__)
        except (ImportError, AttributeError):
            import logging

            logging.debug('aecore wos not able to load config.yaml. Make '
                          'sure that you have placed your config.yaml file in '
                          'your applications root directory. Also, make sure '
                          'thay you have an appengine_config.py file in the '
                          'root directory as well. Fore, aecore uses this '
                          'file to locate your config.yaml')
            return None
        file_path = os.path.join(root_dir, 'config.yaml')
        stream = open(file_path, 'r')
        rout_config = yaml.load(stream)
        return rout_config
    load_route_config = _load_route_config

    @staticmethod
    def _load_app_config(app_name):
        import os
        import yaml

        try:
            app_dir = os.path.dirname(__import__(app_name).__file__)
            file_path = os.path.join(app_dir, 'config.yaml')
            stream = open(file_path, 'r')
            return yaml.load(stream)
        except ImportError:
            return None
    load_app_config = _load_app_config

    @classmethod
    def load_config_files(cls):
        import utils
        root_cfg = cls._load_route_config()
        all_cfg = {}
        if root_cfg is not None and 'installed_apps' in root_cfg:
            for app in root_cfg['installed_apps']:
                app_cfg = cls._load_app_config(app)
                if app_cfg: all_cfg = dict(all_cfg.items() + app_cfg.items())
        return utils.merge_dicts(all_cfg, root_cfg)

    @classmethod
    def create(cls, id, default):
        obj = cls(id=id)
        obj.data = default
        # add the id here for use in the admin
        obj.data['id'] = id
        obj.put()
        return obj

    @classmethod
    def get(cls, id):
        obj = cls.get_by_id(id)
        if obj is None:
            default_config = cls.load_config_files()
            obj = cls.create(id, default_config[id])
        if obj.data is None: return None
        return dotdict(obj.data)


class Session(ndb.Model):
    session_id = ndb.StringProperty('sid')
    user_id = ndb.StringProperty('uid')
    updated = ndb.DateTimeProperty('u', auto_now=True)
    data = ndb.PickleProperty('c', compressed=True, default={})

    @staticmethod
    def _generate_sid():
        return security.generate_random_string(entropy=128)

    @staticmethod
    def _serializer():
        config = Config.get('aecore')
        #  hmac will not accept unicode. So we have to convert the key to ascii
        return securecookie.SecureCookieSerializer(
            config.secret_key.encode('ascii'))

    def get_id(self):
        """Returns this user's unique ID, which can be an integer or string."""
        return str(self.key.id())

    def hash(self):
        """
        Creates a unique hash from the session.
        This will be used to check for session changes.
        :return: A unique hash for the session
        """
        return hash(str(self))

    def serialize(self):
        cookie_key = Config.get('aecore').cookie_key
        values = self.to_dict(include=['session_id', 'user_id'])
        return self._serializer().serialize(cookie_key, values)

    @classmethod
    def deserialize(cls, value):
        cookie_key = Config.get('aecore').cookie_key
        return cls._serializer().deserialize(cookie_key, value)

    @classmethod
    def get_by_value(cls, value):
        v = cls.deserialize(value)
        try:
            return cls.get_by_sid(v['session_id'])
        except Exception:
            return None

    @classmethod
    def get_by_sid(cls, sid):
        return cls.get_by_id(sid)

    @classmethod
    def upgrade_to_user_session(cls, session_id, user_id):
        old_session = cls.get_by_sid(session_id)
        new_session = cls.create(user_id=user_id, data=old_session.data)
        old_session.key.delete()
        return new_session

    @classmethod
    def get_by_user_id(cls, user_id):
        # TODO: make sure that the user doesn't have multiple sessions
        user_id = str(user_id)
        return cls.query(cls.user_id == user_id).get()

    @classmethod
    def create(cls, user_id=None, **kwargs):
        if user_id is None:
            session_id = cls._generate_sid()
        else:
            session_id = user_id = str(user_id)
        session = cls(id=session_id, session_id=session_id,
            user_id=user_id, **kwargs)
        session.put()
        return session

    @classmethod
    def remove_inactive(cls, days_ago=30, now=None):
        import datetime
        # for testing we want to be able to pass a value for now.
        now = now or datetime.datetime.now()
        dtd = now + datetime.timedelta(-days_ago)
        for s in cls.query(cls.updated < dtd).fetch():
            s.key.delete()


class UserProfile(polymodel.PolyModel):
#    options = ndb.JsonProperty()
    person = ndb.LocalStructuredProperty(types.Person)
    person_raw = ndb.JsonProperty('pr', indexed=False)
    updated = ndb.DateTimeProperty('u', auto_now=True, indexed=False)
#    user_id = ndb.StringProperty('uid')
    owner_ids = ndb.StringProperty('o', repeated=True)
    data = ndb.JsonProperty('d', indexed=False)

    provider = None
    provider_url = None

    @staticmethod
    def generate_auth_id(provider, uid, subprovider=None):
        """Standardized generator for auth_ids

        :param provider:
            A String representing the provider of the id.
            E.g.
            - 'google'
            - 'facebook'
            - 'appengine_openid'
            - 'twitter'
        :param uid:
            A String representing a unique id generated by the Provider.
            I.e. a user id.
        :param subprovider:
            An Optional String representing a more granular subdivision of a provider.
            i.e. a appengine_openid has subproviders for Google, Yahoo, AOL etc.
        :return:
            A concatenated String in the following form:
            '{provider}#{subprovider}:{uid}'
            E.g.
            - 'facebook:1111111111'
            - 'twitter:1111111111'
            - 'appengine_google#yahoo:1111111111'
            - 'appengine_google#google:1111111111'
        """
        if subprovider is not None:
            provider = '{0}#{1}'.format(provider, subprovider)
        return '{0}:{1}'.format(provider, uid)

    def get_provider(self):
        return self.key.id().split(":")[0]

    def get_id(self):
        return str(self.key.id())

    def add_owner_id(self, user_id):
        """A helper method to add additional owners

        :param user_id:
            a ``User.key.id()``
        :returns:
            ``self``
        """
        # As a convention owner_ids are stored as strings.
        owner_id = str(user_id)
        # If the auth_id is already in the list return True
        if owner_id in self.owner_ids:
            return self
        self.owner_ids.append(owner_id)
        return self

    def is_owner(self, user_id):
        """This method is used for authorization. to determine if a
        User has permission to modify the UserProfile.

        :param user_id:
            the User.key.id() to test for ownership
        :return:
            a boolean True if owner. Otherwise False
        """
        user_id = str(user_id)
        if user_id in self.owner_ids:
            return True
        return False

    def merge_profile(self, profile_from):
        """
        Merges missing attributes from one profile to anther. This method
        is non-destructive. It only adds properties that missing.

        :param profile_from:
            A ``dict`` representing the profile from which attributes should come.

        """
        assert isinstance(profile_from, dict), 'profile_form must be a dict'
        # TODO: clean this up. Account for nested list / dicts
        if self.data is None:
            self.data = profile_from
            self.data['id'] = self.key.id()
            self.data['provider'] = 'master'
            self.put()
            return

        profile_to = self.data

        for k, v in profile_from.items():
            if k not in profile_to or profile_to[k] is None:
                profile_to[k] = v
            if isinstance(v, list):
                # if it's not an empty list
                if profile_from[k]:
                    # if the ``profile_to`` dict also has the list we need to merge.
                    if profile_to[k]:
                        # TODO this is wildly inefficient.
                        for i in profile_from[k]:
                            has_attribute = False
                            for ii in profile_to[k]:
                                # the name key should be unique so search for that
                                if ii['name'] == i['name']:
                                    has_attribute = True
                                    break
                            if not has_attribute:
                                profile_to[k].append(i)
                    # otherwise just copy it.
                    else:
                        profile_to[k] = profile_from[k]

        self.put()
        return

    def get_person(self, **kwargs):
        """
        person = types.Person()

        ## Required ##
        person.provider             = None # u'facebook'
        person.id                   = None # u'12345'
        person.name                 = None # u'Mr. Joseph Robert Smarr, Esq'

        ### Accounts ###
        # You are required to create an account object for the providers
        # account. You may optionally add additional account, too.
        account                     = types.Account()
        account.name                = None # u'facebook'
        account.url                 = None # u'facebook.com'
        account.userid              = None # u'123456789'
        account.username            = None # u'scotchmedia'
        person.accounts             = [account]

        ## Optional ##

        ### Name Details ###
        person.givenName            = None # u'Joseph'
        person.additionalName       = None # u'Robert'
        person.familyName           = None # u'Smarr'
        person.honorificPrefix      = None # u'Mr.'
        person.honorificSuffix      = None # u'Esq.'

        ### Singular Fields ###
        person.url                  = None # u'http://facebook.com/username'
        person.birthDate            = None # datetime.datetime(1969, 7, 20, 1, 12, 3, 723097)
        person.description          = None # u'Longer description'
        person.email                = None # u'test@example.com'
        person.image                = None # u'http://awesome.jpg.to/'
        person.gender               = None # u'male'
        person.locale               = None # u'en_US'
        person.location             = None # types.Place(name=u'Springfield, VT')
        person.relationshipStatus   = None # u'single'
        person.published            = None # datetime.datetime(2010, 7, 20, 1, 12, 3, 723097)
        person.updated              = None # datetime.datetime(2011, 7, 20, 1, 12, 3, 723097)
        person.utcOffset            = None # u'-06:00'
        person.verified             = None # True

        ### PostalAddress ###
        address                     = types.PostalAddress()
        address.type                = None # u'work'
        address.streetAddress       = None # u'742 Evergreen Terrace\nSuite 123'
        address.addressLocality     = None # u'Springfield'
        address.addressRegion       = None # u'VT'
        address.postalCode          = None # u'12345'
        address.addressCountry      = None # types.Country(name=u'USA')
        person.address              = address

        ## List Fields ##

        ### Affiliation ###
        #### Work ####
        work                        = types.Organization()
        work.address                = address
        work.name                   = None # u'Scotch Media, LLC.'
        work.url                    = None # u'http://www.scotchmedia.com'
        work.description            = None # u'neat.'
        work.location               = None # types.Place(name=u'Kansas USA')
        affiliation1                = types.Affiliation()
        affiliation1.name           = None # u'CCO'
        affiliation1.description    = None # u'Chief Creative Officer'
        affiliation1.organization   = work # types.Organization()
        affiliation1.department     = None # u'Creative'
        affiliation1.startDate      = None # datetime.datetime(2010, 1, 14, 10, 12, 3, 723097)
        affiliation1.endDate        = None # datetime.datetime(2012, 1, 14, 10, 12, 3, 723097)
        affiliation1.location       = None # types.Place(name=u'Kansas USA')
        #### School ####
        school                      = types.Organization()
        school.address              = address
        school.name                 = None # u'FHSU'
        school.url                  = None # u'http://www.fhsu.edu'
        school.description          = None # u'tiger'
        school.location             = None # types.Place(name=u'Hays, Kansas USA')
        affiliation2                = types.Affiliation()
        affiliation2.name           = None # u'BFA'
        affiliation2.department     = None # u'Graphic Design'
        affiliation2.description    = None # u'BFA Emphasis in Graphic Design'
        affiliation2.startDate      = None # datetime.datetime(2010, 1, 14, 10, 12, 3, 723097)
        affiliation2.endDate        = None # datetime.datetime(2012, 1, 14, 10, 12, 3, 723097)
        affiliation2.location       = None # types.Place(name=u'Kansas USA')
        # This next may not be necessary in the future
        affiliation2.itemtype       = u'EducationalOrganization' # u'EducationalOrganization'
        person.affiliations         = [affiliation1, affiliation2]

        ### languages Spoken ###
        language1                   = types.Language()
        language1.name              = None # u'English'
        language1.proficiency       = None # 5
        person.languagesSpoken      = [language1]

        ### Certifications ###
        certification1              = types.Certification()
        certification1.type         = None # u'license'
        certification1.name         = None # u'medical'
        certification1.authority    = None # u'Texas Medical Board"
        certification1.number       = None # u'12345'
        certification1.startDate    = None # datetime.datetime(2002, 7, 20, 1, 12, 3, 723097)
        certification1.endDate      = None # datetime.datetime(2012, 7, 20, 1, 12, 3, 723097)
        person.certifications       = [certification1]

        ### Skills ###
        skill1                      = types.Skill()
        skill1.name                 = None # u'python'
        skill1.years                = None # 2
        skill1.proficiency          = None # 3
        person.skills               = [skill1]

        ### URLs ###
        url                         = types.URL()
        url.description             = None # u'work'
        url.url                     = None # u'http://www.scotchmedia.com'
        url.primary                 = None # True
        person.urls                 = [url]

        ### Emails ###
        email                       = types.Email()
        email.address               = None # u'example1@example.com'
        email.description           = None # u'home'
        email.primary               = None # True
        email.verified              = None # True
        person.emails               = [email]

        ### IMs ###
        im                          = types.IM()
        im.address                  = None # u'im1@example.com'
        im.description              = None # u'aim'
        im.primary                  = None # True
        im.verified                 = None # False
        person.ims                  = [im]

        self.person = person
        return self
        """
        raise NotImplementedError()

    def populate_missing(self, people_list):
        assert isinstance(people_list, list), 'people_list must be a list'

    @classmethod
    def _get_kind(cls):
        return 'UserProfile'

    @classmethod
    def get_by_user_id(cls, user_id):
        user_id = str(user_id)
        return cls.query(cls.owner_ids == user_id).fetch(10)

    @classmethod
    def _get_key(cls, provider, uid, subprovider=None):
        """Standardized generator for auth_ids

        :param provider:
            A String representing the provider of the id.
            E.g.
            - 'google'
            - 'facebook'
            - 'appengine_openid'
            - 'twitter'
        :param uid:
            A String representing a unique id generated by the Provider.
            I.e. a user id.
        :param subprovider:
            An Optional String representing a more granular subdivision of a provider.
            i.e. a appengine_openid has subproviders for Google, Yahoo, AOL etc.
        :return:
            A concatenated String in the following form:
            '{provider}#{subprovider}:{uid}'
            E.g.
            - 'facebook:1111111111'
            - 'twitter:1111111111'
            - 'appengine_google#yahoo:1111111111'
            - 'appengine_google#google:1111111111'
            ``ndb.Key`` containing a string id in the following format:
            ``{provider}#{subprovider}:{uid}.``
        """
        return ndb.Key(cls, cls.generate_auth_id(provider, uid, subprovider))
    get_key = _get_key

    @classmethod
    def _create(cls, provider, uid):
        obj = cls()
        obj._key = cls._get_key(provider, uid)
        obj.put()
        return obj
    create = _create

    @classmethod
    def get_or_create(cls, provider, uid):
        obj = cls.get_key(provider, uid).get()
        if obj is None:
            obj = cls._create(provider, uid)
        return obj


class UserToken(ndb.Model):
    """Stores validation tokens for users."""
    created = ndb.DateTimeProperty('c', auto_now_add=True)

    @property
    def user_id(self):
        return int(self.key.id().split(".")[0])

    @property
    def subject(self):
        return self.key.id().split(".")[1]

    @property
    def token(self):
        return self.key.id().split(".")[2]

    @classmethod
    def get_key(cls, user, subject, random_token):
        """Returns a token key.

        :param user:
            User unique ID.
        :param subject:
            The subject of the key. Examples:

            - 'auth'
            - 'signup'
        :param random_token:
            Randomly generated token.
        :returns:
            ``model.Key`` containing a string id in the following format:
            ``{user_id}.{subject}.{token}.``
        """
        return ndb.Key(cls, '%s.%s.%s' % (user, subject, random_token))

    @classmethod
    def create(cls, user, subject, random_token=None):
        """Creates a new token for the given user.

        :param user:
            User unique ID.
        :param subject:
            The subject of the key. Examples:

            - 'auth'
            - 'signup'
        :param random_token:
            Optionally an existing token may be provided.
            If None, a random token will be generated.
        :returns:
            The newly created :class:`UserToken`.
        """
        random_token = random_token or security.generate_random_string(
            entropy=128)
        key = cls.get_key(user, subject, random_token)
        entity = cls(key=key)
        entity.put()
        return entity


class UserEmail(ndb.Model):
    """
    This class is Simply a look up table. It allows for query by email address.
    An Email address must be unique, i.e. an email address can only belong to
    one User.

    """
    user_id = ndb.StringProperty('uid')

    @classmethod
    def get_by_user_id(cls, user_id):
        """
        Helper method to look up by ``UserEmail``s by user_id

        :param user_id:
            ``User.key.id()`` to search by
        :return:
            list of ``UserEmail`` that have the specified user_id
        """
        return cls.query(cls.user_id == user_id).fetch()

    @classmethod
    def create(cls, email, user_id):
        """
        Creates a ``UserEmail`` given an email and ``User.key.id()``

        :param email:
            string representing the email address of the user
        :param user_id:
            string representing the ``User.key.id()`` of the User
        """
        email = email.lower()
        obj = cls(id=email, user_id=user_id)
        obj.put()

    @classmethod
    def get_or_create(cls, email, user_id):
        """
        Given an email and user_id the is method first searches for an existing
        account if one if found it returns it, otherwise a new on is created and
        saved to the datastore.

        :param email:
            string representing the email address of the user
        :param user_id:
            string representing the ``User.key.id()`` of the User
        :return:
            the newly created ``UserEmail``
        """
        email = email.lower()
        obj = cls.get_by_id(email)
        if obj is None:
            obj = cls(id=email, user_id=user_id)
            obj.put()
        return obj


class User(ndb.Model):
    """Stores user authentication credentials or authorization ids."""

    user_profile_model = UserProfile
#    user_token_model = UserToken

    created = ndb.DateTimeProperty('c', auto_now_add=True)
    updated = ndb.DateTimeProperty('u', auto_now=True)

    auth_ids = ndb.StringProperty('a', repeated=True)
    password = ndb.StringProperty('w', indexed=False)

    # ``aecore.types.Person`` representing the user's profile
#    data = ndb.JsonProperty('d')
#    data = ndb.StructuredProperty(types.Person)
    # Add roles for Role base Authorization
    roles = ndb.StringProperty('r', repeated=True)
    # Add perms for Resource based Authorization
    perms = ndb.StringProperty('p', repeated=True)

    def get_id(self):
        """
        helper method return the string representation of the ``key.id()``

        :return:
            string represting the ``key.id()`` of the model
        """
        return str(self.key.id())

    def _add_roll(self, roll):
        """
        A helper method to add additional rolls to a User

        :param roll:
            a string representing the roll for the user
        :returns:
            ``self``
        """
        roll = roll.lower()
        # If the roll is already in the list return True
        if roll in self.roles:
            return self
        else:
            self.roles.append(roll)
            return self
    add_roll = _add_roll

    def has_roll(self, role):
        """
        A helper method that evaluates the presents of a Role in the
        User's roles property.

        :param role:
            Authorization role e.g. 'admin', 'mod'
        :return:
            A boolean - ``True`` if the User has the role, ``False`` if not.
        """
        role = role.lower()
        return role in self.roles

    def _add_perm(self, access_type, kind_name):
        """
        A helper method to add additional permissions to a User

        :param access_type:
            The right being granted. Must be one of the following:
              'create', 'read', 'update', 'delete'
        :param kind_name:
            a string representing the datastore kind of the model
        :returns:
            ``self``
        """
        assert access_type in ['create', 'read', 'update', 'delete'],\
        'the access_type must be one of the following '\
        'create, read, update, delete'

        key = '{}_{}'.format(access_type, kind_name)
        # If the perms is already in the list return True
        if key in self.perms:
            return self
        else:
            self.perms.append(key)
            return self
    add_perm = _add_perm

    def get_auth_id(self, provider):
        for k in self.auth_ids:
            if k.startswith(provider):
                return k
        return None

    def _add_auth_id(self, auth_id):
        """
        A helper method to add additional auth_ids to a User

        :param auth_id:
            a ``UserProfile.key.id()``
        :returns:
            ``self``
        """
        # If the auth_id is already in the list return True
        if auth_id in self.auth_ids:
            return self
        if self.__class__.get_by_auth_id(auth_id):
            raise DuplicatePropertyError(value=[auth_id])
        else:
            self.auth_ids.append(auth_id)
            return self
    add_auth_id = _add_auth_id

    def _check_password(self, password):
        # TODO switch password encryption to bcrypt
        """
        Validate that the user supplied password matches the the hashed
        password saved to the datastore.

        :param password: string representing the password
        :return: boolean True if match False if not.
        """
        return security.check_password_hash(password, self.password)
    check_password = _check_password

    def _set_password(self, password):
        # TODO switch password encryption to bcrypt
        """
        Set the User's password attribute to the hashed password generated
        from the supplied password string

        :param password: a string representing the password
        """
        self.password = security.generate_password_hash(password, length=12)
    set_password = _set_password

    def has_profile(self, provider):
        """
        A test that indicates if the provider is present in the User
        auth_ids list.

        :param provider:
        :return: boolean True if the User has a auth_id for the supplied
            ``provider`` string
        """
        for a in self.auth_ids:
            if a.split(":")[0].startswith(provider):
                return True
        return False

    def get_master_profile(self):
        """
        Get or create the master UserProfile for the user.

        :return:``UserProfile``
        """
        id = self.user_profile_model.generate_auth_id('master', self.key.id())
        p = ndb.Key(self.user_profile_model, id).get()
        if p is None:
            p = self.user_profile_model(id=id)
            p.owner_ids = [str(self.key.id())]
            p.put()
        return p

    def get_profile(self, provider=None):
        """
        Retrieves a single profile based on the provider.

        :param provider: a string representing the name of the provider.
            E.g. google, facebook.
        :return: ``UserProfile``
        """

        for a in self.auth_ids:
            pro = a.split(":")[0]
            if pro.startswith(provider):
                return ndb.Key(self.user_profile_model, a).get()
        return False

    def get_profiles(self):
        """
        A helper method to retrieve the ``UserProfile``s created from the
        user's ``auth_ids``

        :return: ``list`` of ``UserProfile``
        """
        keys = [ndb.Key(self.user_profile_model, aid)
                for aid in self.auth_ids]
        return ndb.get_multi(keys)


    @classmethod
    def _get_by_auth_id(cls, auth_id):
        """
        Returns a user object based on a auth_id.

        :param auth_id:
            a ``UserProfile.key``
        :returns:
            A user object.
        """
        return cls.query(cls.auth_ids == auth_id).get()
    get_by_auth_id = _get_by_auth_id

    @classmethod
    def _get_by_email(cls, email):
        """
        Returns a user object based on an email address.

        :param email:
            a string representing an email address
        :returns:
            A user object.
        """
        auth_id = 'own:{}'.format(email.lower())
        return cls.query(cls.auth_ids == auth_id).get()
    get_by_auth_id = _get_by_auth_id

    @classmethod
    def _create(cls, auth_id=None, **user_values):
        """
        Creates a new user.

        :param user_values:
            Keyword arguments to create a new user entity.
        :returns:
            The crated user
        """
        if auth_id is not None:
            if cls._get_by_auth_id(auth_id):
                raise DuplicatePropertyError(value=[auth_id])
            user_values['auth_ids'] = [auth_id]
        user = cls(**user_values)

        user.put()
        # Were calling this method to ensure that a UserProfile is created
        # for the user.
        user.get_master_profile()
        return user
    create = _create

    @classmethod
    def get_or_create_by_auth_id(cls, auth_id):
        # TODO this method introduces a potential race condition.
        # Attribute queries are not strongly consistent.
        user = cls._get_by_auth_id(auth_id)
        if user is None:
            user = cls._create(auth_id)
        return user

    @classmethod
    def get_or_create_by_email(cls, email):
        # TODO this method introduces a potential race condition.
        # Attribute queries are not strongly consistent.
        user = cls._get_by_email(email)
        if user is None:
            auth_id = 'own:{}'.format(email.lower())
            user = cls._create(auth_id)
        return user


class Webapp2User(User):
    """
    User that is compatible with webapp2_extras.appengine.auth.models.User

    """

    user_profile_model = UserProfile
    #    user_token_model = UserToken

    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    # ``aecore.types.Person`` representing the user's profile
    data = ndb.JsonProperty()

    auth_ids = ndb.StringProperty(repeated=True)
    password = ndb.StringProperty(indexed=False)

    # Add roles for Role base Authorization
    roles = ndb.StringProperty(repeated=True)
    # Add perms for Resource based Authorization
    perms = ndb.StringProperty(repeated=True)