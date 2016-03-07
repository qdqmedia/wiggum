import logging

from django.conf import settings

from .login_success import (CreateJWTAction,
                            RedirectToCloneJWTSessionAction,
                            SetJWTOnCookieAction)

from metrics import inc_password_resets

logger = logging.getLogger(__name__)


class ResetPassBaseAction(object):
    """Reset password base action"""
    def do(self, action_context, view, user, *args, **kwargs):
        return action_context


class CreateJwtOnViewOnPassResetAction(ResetPassBaseAction):
    """Generates and sets the jwt token on the cookie"""

    def do(self, action_context, view, user, *args, **kwargs):
        if settings.LOGIN_ON_PASSWORD_RESET:
            # Set jwt
            a = CreateJWTAction()
            action_context = a.do(action_context, view, user, *args, **kwargs)

        return super().do(action_context, view, user, *args, **kwargs)


class RedirectToCloneJWTSessionOnPassResetAction(ResetPassBaseAction):
    """Redirects to the clone view to set the token on every domain"""

    def do(self, action_context, view, user, *args, **kwargs):
        if settings.LOGIN_ON_PASSWORD_RESET:
            # Clone token on domains
            a = RedirectToCloneJWTSessionAction()
            action_context = a.do(action_context, view, user, *args, **kwargs)

        return super().do(action_context, view, user, *args, **kwargs)


class SetJWTOnCookieOnPassResetAction(ResetPassBaseAction):
    """ Sets the JWT cookie on the request """

    def do(self, action_context, view, user, *args, **kwargs):
        if settings.LOGIN_ON_PASSWORD_RESET:
            # Set cookie on final response
            a = SetJWTOnCookieAction()
            action_context = a.do(action_context, view, user, *args, **kwargs)

        return super().do(action_context, view, user, *args, **kwargs)


class PasswordResetMetricAction(ResetPassBaseAction):
    def do(self, action_context, view, user, *args, **kwargs):
        inc_password_resets()
        return super().do(action_context, view, user, *args, **kwargs)
