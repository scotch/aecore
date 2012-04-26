import webapp2
from webapp2_extras import jinja2
from aecore.models import Config
from aecore.middleware import Request


class Jinja2Handler(webapp2.RequestHandler):

    def dispatch(self):
        self.request.__class__ = Request
        webapp2.RequestHandler.dispatch(self)

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def get_messages(self, key='_messages'):
        try:
            return self.request.session.data.pop(key)
        except KeyError:
            return None

    def add_message(self, message, level=None, key='_messages'):
        self.request.add_message(message, level, key)
        return

    def render_template(self, template_name, template_values=None):
        if template_values is None: template_values = {}
        messages = self.get_messages()
        if messages:
            template_values.update({'messages': messages})

        template_values.update({
            'application': Config.get('application'),
            'user': self.request.user,
            'session': self.request.session,
            })
        self.response.write(self.jinja2.render_template(
            template_name, **template_values))