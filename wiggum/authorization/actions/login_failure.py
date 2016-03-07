from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from metrics import inc_failed_login

class LoginFailureBaseAction(object):
    """Login failure base action"""
    def do(self, action_context, view, *args, **kwargs):
        return action_context


class AuthenticationErrorMessageAction(LoginFailureBaseAction):
    """Set a flash message with the failure login"""

    def do(self, action_context, view, *args, **kwargs):
        # Means failure on login
        if not action_context.extra_context.get("user_authenticated"):
            messages.add_message(action_context.request, messages.ERROR,
                                 _("Authentication error"))

        return super().do(action_context, view, *args, **kwargs)


class LoginFailureMetricAction(LoginFailureBaseAction):
    """Set login failure metric"""

    def do(self, action_context, view, *args, **kwargs):
        inc_failed_login()
        return super().do(action_context, view, *args, **kwargs)
