import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from .. import jwt_utils
from ..utils import str_to_class, get_redirect_url

logger = logging.getLogger(__name__)


# TODO: Remove this duplicated code from Loginview
auth_backends = settings.WIGGUM_AUTHENTICATION_BACKENDS
def get_authentication_backends():
    return [str_to_class(backend)() for backend in auth_backends]


class LoginPreCheckBaseAction(object):
    """Login pre form check base action"""

    def do(self, action_context, view, *args, **kwargs):
        """user will be none if the user was not authenticated"""
        return action_context

class ForceLoginFormAction(LoginPreCheckBaseAction):
    """ Breaks the chain to force the the login form despite the user is logged
        already
    """
    def do(self, action_context, view, *args, **kwargs):
        if settings.FORCE_LOGIN_FORM:
            action_context.break_chain = True
            logger.debug("Forcing login form")

        return super().do(action_context, view, *args, **kwargs)


class CheckUserAuthenticatedAlreadyAction(LoginPreCheckBaseAction):
    """ Checks if the user is already authenticated"""

    def do(self, action_context, view, *args, **kwargs):
        """Creates the appropiate response to return"""

        # If need to force login then always show the login form
        credential_data = {
            'request': action_context.request,
        }
        backends = get_authentication_backends()

        for i in backends:
            user_authenticated = i.authenticate(**credential_data)
            if user_authenticated:
                action_context.extra_context['jwt'] = action_context.request.\
                    COOKIES.get(settings.JWT_COOKIE_NAME, None)
                action_context.extra_context['user_authenticated'] = True
                action_context.extra_context['user'] = user_authenticated

                # Do not break chain, we need to check the version of the token
                action_context.response = HttpResponseRedirect(
                    action_context.extra_context['redirect_url'])

        return super().do(action_context, view, *args, **kwargs)


class CheckValidJWTVersionAction(LoginPreCheckBaseAction):
    """ Checks if the jwt token version is correct, if not then this token is
        destroyed (logout)
    """

    def do(self, action_context, view, *args, **kwargs):
        jwt = action_context.extra_context.get('jwt')
        if jwt and settings.JWT_DESTROY_TOKEN_ON_LESSER_VERSION:
            jwt_version = float(jwt_utils.decode_jwt(jwt).get('version', 0))

            if jwt_version < settings.JWT_MINIMUM_VERSION:
                logout_url = reverse("auth:logout")
                action_context.extra_context['invalid_jwt_version'] = True

                # Check if redirection is needed (checks all the valid redirects)
                redirect_uri = get_redirect_url(action_context.request)

                if redirect_uri:
                    redirect_param = settings.REDIRECT_URL_VALID_PARAMS[0]
                    logout_url = "{0}?{1}={2}".format(
                        logout_url, redirect_param, redirect_uri)
                msg = ("JWT version is invalid (token:{0}) "
                       "(minimum: {1})").format(jwt_version,
                       settings.JWT_MINIMUM_VERSION)
                logger.info(msg)
                action_context.response = HttpResponseRedirect(logout_url)

        return super().do(action_context, view, *args, **kwargs)
