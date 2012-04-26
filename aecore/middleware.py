from aecore import utils
from aecore import models
from webob import Response as WebobResponse
from webob import Request as WebobRequest


class Response(WebobResponse):

    def _save_session(self):
        session = self.request.session
        # Compare the hash that we set in load_session to the current one.
        # We only save the session and cookie if this value has changed.
        if self.request.session_hash == session.hash():
            return session
        session.put()
        # If we have a user_id we want to updated the
        # session to use the user_id as the key.
        if session.user_id is not None:
            session_id = session.key.id()
            if session_id != session.user_id:
                session = models.Session.upgrade_to_user_session(
                    session_id, session.user_id)
        # load cookie config
        config = models.Config.get('aecore')
        max_age = int(config.cookie_max_age) if config.cookie_max_age else None
        self.set_cookie(
            config.cookie_key.encode('ascii'),
            value=session.serialize(),
            max_age=max_age,
            path=config.cookie_path.encode('ascii'),
            domain=config.cookie_domain,
            secure=config.cookie_secure,
            httponly=config.cookie_httponly)
        return self

    def _save_user(self):
        # TODO: save user if modified.
        pass

    def _set_redirect(self, location, code=307):
        # TODO this needs to be improved
        # exc.HTTPTemporaryRedirect(location=location)
        self.headers['Location'] = location
        self.status = code
    set_redirect = _set_redirect

class Request(WebobRequest):

    ResponseClass = Response

    def _load_session(self):
        config = models.Config.get('aecore')
        value = self.cookies.get(config.cookie_key)
        session = None
        if value:
            session = models.Session.get_by_value(value)
        if session is not None:
            # Create a hash for later comparison,
            # to determine if a put() is required
            session_hash = session.hash()
        else:
            session = models.Session.create()
            # set this to False to ensure a cookie
            # is saved later in the response.
            session_hash = '0'
        self.session = session
        self.session_hash = session_hash
        return self
    load_session = _load_session

    def _get_user_model(self):
        try:
            return utils.import_class(self._config.user_model)
        except ImportError, e:
            raise Exception('The following error occurred while attempting to '\
                            'import your custom user model: {}'.format(e))
        except AttributeError:
            # This is allows for test with out the need to pass a _config.
            return models.User
    get_user_model = _get_user_model

    def _load_user(self, user_id=None):
        user = None
        user_model = self._get_user_model()
        if user_id is None and self.session is not None and self.session.user_id:
            user_id = self.session.user_id
        if user_id is not None:
            user = user_model.get_by_id(int(user_id))
        # Add user to session
        self.session.user_id = user.get_id() if user else None
        self.user = user
        return self
    load_user = _load_user

    def _add_message(self, message, level=None, key='_messages'):
        if not self.session.data.get(key):
            self.session.data[key] = []
        return self.session.data[key].append({
            'message': message, 'level': level})
    add_message = _add_message

    def _get_messages(self, key='_messages'):
        try:
            return self.session.data.pop(key)
        except KeyError:
            pass
    get_messages = _get_messages

    def _set_redirect_url(self, url=None):
        if url is not None:
            next_uri = url
        else:
            next_uri = self.GET.get('next')
        if next_uri is not None:
            self.session.data['_redirect_url'] = next_uri
    set_redirect_url = _set_redirect_url

    def _get_redirect_url(self):
        try:
            return self.session.data.pop('_redirect_url').encode('utf-8')
        except KeyError:
            return None
    get_redirect_url = _get_redirect_url


class AECoreMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # If the request is to the admin, return
        if environ['PATH_INFO'].startswith('/_ah/'):
            return self.app(environ, start_response)

        # load session
        request = Request(environ)
        request.load_session()
        request.load_user()
        request.set_redirect_url()
        response = request.get_response(self.app)
        response.request = request

        # Save session, return response
        response._save_session()

        # see if a redirect as been saved to the session
        redirect = response.request.get_redirect_url()

        if redirect:
            response.set_redirect(redirect)
        return response(environ, start_response)


