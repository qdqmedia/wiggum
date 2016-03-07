import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from .. import jwt_utils
from ..utils import create_next_domains_url, get_redirect_url
from .mixins import JWTCookieActionMixin
from metrics import inc_succeeded_login

logger = logging.getLogger(__name__)


class LoginSuccessBaseAction(object):
    """Login success base action"""
    def do(self, action_context, view, user, *args, **kwargs):
        """user will be none if the user was not authenticated"""
        return action_context


class CreateJWTAction(LoginSuccessBaseAction):
    """ Creates the jwt token"""

    def do(self, action_context, view, user, *args, **kwargs):
        """Sets the jwt token"""
        if user:
            action_context.extra_context['jwt'] = jwt_utils.create_jwt(user)

        return super().do(action_context, view, user, *args, **kwargs)


class RedirectToCloneJWTSessionAction(LoginSuccessBaseAction):
    """ Sets the url to clone de cookie on the response"""

    def do(self, action_context, view, user, *args, **kwargs):
        redirect_uri = None

        # If cookie cloning is activated then
        user_authenticated = action_context.extra_context['user_authenticated']
        if settings.JWT_COOKIE_CLONE and user_authenticated:
            # Get redirection uri
            redirect_uri = get_redirect_url(action_context.request)

            if not redirect_uri:
                redirect_uri = view.success_url

            params = {
                settings.REDIRECT_URL_VALID_PARAMS[0]: redirect_uri
            }

            # Remove the current domain
            clone_domains = list(settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT)

            try:
                clone_domains.remove(
                    action_context.request.META.get('HTTP_HOST'))
            except ValueError:
                # Maybe the domain is not on clone domains list but is a valid
                # wiggum domain, if not then raise an exception
                if action_context.request.META.get('HTTP_HOST') not in\
                   settings.ALLOWED_HOSTS:
                    logger.error("Not a valid wiggum domain {0}".format(
                        action_context.request.META.get('HTTP_HOST')),
                        extra={'request': action_context.request})

                    raise ValueError("Not a valid wiggum domain {0}".format(
                        action_context.request.META.get('HTTP_HOST')
                    ))

            next_domain = clone_domains.pop(0)
            jwt = action_context.extra_context.get('jwt')
            if not jwt:
                logger.error("Not jwt token to clone",
                             extra={'request': action_context.request})

                raise ValueError("Not jwt token to clone")

            url_path = reverse('auth:clone-cookie',
                               kwargs={'token': jwt})

            uri = create_next_domains_url(
                path=url_path,
                scheme='http' if settings.DEBUG else "https",
                domain=next_domain,
                query_params=params,
                clone_domains=clone_domains)

        else:
            uri = get_redirect_url(action_context.request)

        # If we have the uri then we redirect to the cloned url response
        if uri:
            action_context.response = HttpResponseRedirect(uri)

        return super().do(action_context, view, user, *args, **kwargs)


class SetJWTOnCookieAction(JWTCookieActionMixin, LoginSuccessBaseAction):
    """ Set the cookie on the response
        Note: This action should be the last one (it modifies the final
              response)
    """

    def do(self, action_context, view, user=None, *args, **kwargs):
        """Sets the jwt token without calculating"""
        # If not in the argument check on the view
        jwt = action_context.extra_context.get('jwt')
        if not jwt:
            logger.error("Not jwt token to set",
                         extra={'request': action_context.request})

            raise ValueError("Not jwt token to set")

        # Get the host for the cookie
        host = self.get_host(action_context.request)

        # Get the expiration delta (impersonate?)
        if jwt_utils.decode_jwt(jwt).get("impersonate"):
            expiration_delta_sec = settings.JWT_IMPERSONATE_COOKIE_EXPIRATION_TIME_DELTA
        else:
            expiration_delta_sec = settings.JWT_COOKIE_EXPIRATION_TIME_DELTA

        # Set the response
        action_context.response = jwt_utils.set_jwt_cookie_to_response(
            response=action_context.response,
            cookie_key=settings.JWT_COOKIE_NAME,
            encoded_jwt=jwt,
            expiration_delta_sec=expiration_delta_sec,
            domain=host,
            secure=settings.JWT_COOKIE_ONLY_HTTPS)

        logger.info("JWT token set for user {0} on {1}".format(user, host))

        return super().do(action_context, view, user, *args, **kwargs)

class LoginSuccessMetricAction(LoginSuccessBaseAction):
    def do(self, action_context, view, user=None, *args, **kwargs):
        inc_succeeded_login()
        return super().do(action_context, view, user, *args, **kwargs)
