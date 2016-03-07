import logging

from django.conf import settings
from django.contrib.auth import logout

from .mixins import JWTCookieActionMixin
from metrics import inc_logouts

logger = logging.getLogger(__name__)


class LogoutBaseAction(object):
    """Logout base action"""
    def do(self, action_context, view, *args, **kwargs):
        return action_context


class DeleteDjangoAuthSessionAction(JWTCookieActionMixin, LogoutBaseAction):
    """ Delete the Django session """

    def do(self, action_context, view, *args, **kwargs):
        """Deletes the Django session"""
        logout(action_context.request)
        return super().do(action_context, view, *args, **kwargs)


class JWTDeleteCookieAction(JWTCookieActionMixin, LogoutBaseAction):
    """ Delete the cookie on the response """

    def do(self, action_context, view, *args, **kwargs):
        """Deletes the jwt token without calculating"""

        # Get the host for the cookie
        host = self.get_host(action_context.request)

        # Delete the cookie
        action_context.response.delete_cookie(key=settings.JWT_COOKIE_NAME,
                                              domain=host)

        logger.info("Delete JWT token on {0}".format(host))
        return super().do(action_context, view, *args, **kwargs)


class LogoutMetricsAction(LogoutBaseAction):
    """ Logouts the metric """

    def do(self, action_context, view, *args, **kwargs):
        """Deletes the Django session"""
        # Only logout on final redirect
        if action_context.extra_context["final_logout"]:
            inc_logouts()
        return super().do(action_context, view, *args, **kwargs)
