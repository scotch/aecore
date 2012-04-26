from aecore.models import Config

def user_required(handler):

    def check_login(self, *args, **kwargs):
        if not self.request.user:
            # If handler has no login_url specified invoke a 403 error
            try:
                # set the redirect url to the current url.
#                self.request.set_redirect_url(self.request.path)
                self.redirect(Config.get('aeauth').login_url, abort=True)
            except (AttributeError, KeyError), e:
                self.abort(403)
        else:
            return handler(self, *args, **kwargs)

    return check_login


def admin_required(handler):

    def check_login(self, *args, **kwargs):
        if not self.request.user or 'admin' not in self.request.user.roles:
            # If handler has no login_url specified invoke a 403 error
            try:
                # set the redirect url to the current url.
#                self.request.set_redirect_url(self.request.path)
                self.redirect(Config.get('aeauth').login_url, abort=True)
            except (AttributeError, KeyError), e:
                self.abort(403)
        else:
            return handler(self, *args, **kwargs)

    return check_login
