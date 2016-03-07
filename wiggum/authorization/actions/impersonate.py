import logging

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect


from .mixins import JWTCookieActionMixin
from .login_pre_check import CheckUserAuthenticatedAlreadyAction
from .. import jwt_utils
from metrics import inc_impersonations

logger = logging.getLogger(__name__)


class ImpersonateBaseAction(object):
    """Logout base action"""
    def do(self, action_context, view, impersonate_user, *args, **kwargs):
        return action_context


class CheckImpersonateActiveAction(ImpersonateBaseAction):
    """ Checks if the app can impersonate """

    def do(self, action_context, view, impersonate_user, *args, **kwargs):
        if not settings.JWT_IMPERSONATE_ENABLE:
            action_context.break_chain = True

            # Add an error message
            messages.add_message(action_context.request, messages.ERROR,
                                 _("Impersonation not active"))

        return super().do(action_context, view, impersonate_user, *args, **kwargs)


class RedirectToLoginIfNotAuthenticatedAction(ImpersonateBaseAction):
    """ Redirects to the login if the user isn't authenticated"""

    def do(self, action_context, view, *args, **kwargs):
        """Creates the appropiate response to return"""

        # We will use this action to check if we have a valid login session
        # if not then redirect to the login
        a = CheckUserAuthenticatedAlreadyAction()
        action_context = a.do(action_context, view, *args, **kwargs)
        # if not authenticated then break teh chain and return to login
        if not action_context.extra_context.get('user_authenticated'):
                action_context.break_chain = True
                url = reverse("auth:login")
                redirect_param = settings.REDIRECT_URL_VALID_PARAMS[0]
                url = "{0}?{1}={2}".format(
                    url,
                    redirect_param,
                    action_context.request.path
                )
                action_context.response = HttpResponseRedirect(url)

        return super().do(action_context, view, *args, **kwargs)

class CheckImpersonatePermissionAction(ImpersonateBaseAction):
    """ Checks if the current user has impersonate permissions """

    def do(self, action_context, view, impersonate_user, *args, **kwargs):
        user = action_context.extra_context.get('user')

        if user and not action_context.extra_context.get('invalid_jwt_version'):
            if not user.project_permissions.filter(
                    key=settings.APP_PERMISSION_KEYS['impersonate']).exists():

                logger.warning("User '{0}' doesn't have permission to impersonate user '{1}'".format(
                    user.id,
                    impersonate_user.id))
                action_context.break_chain = True

                # Add an error message
                messages.add_message(
                    action_context.request,
                    messages.ERROR,
                    _("You don't have impersonation permission"))

        return super().do(action_context, view, impersonate_user, *args, **kwargs)


class CheckImpersonateSameUserAction(ImpersonateBaseAction):
    """ Checks if the User is impersonating the same user """

    def do(self, action_context, view, impersonate_user, *args, **kwargs):
        user = action_context.extra_context.get('user')
        if impersonate_user.id == user.id:
            action_context.break_chain = True
            # Add an error message
            logger.warning("Can't impersonate yourself")
            messages.add_message(action_context.request, messages.ERROR,
                                 _("Can't impersonate yourself"))

        return super().do(action_context, view, impersonate_user, *args, **kwargs)


class CreateImpersonateJWTAction(ImpersonateBaseAction):
    """ Creates the impersonate jwt token"""

    def do(self, action_context, view, impersonate_user, *args, **kwargs):
        """Sets the impersonate jwt token"""
        if impersonate_user:
            extra_data = {
                'impersonate': True,
                'real_user_id': action_context.extra_context['user'].id
            }
            action_context.extra_context['jwt'] = jwt_utils.create_jwt(
                impersonate_user,
                expiration_time=settings.JWT_IMPERSONATE_EXPIRATION_TIME_DELTA,
                extra_data=extra_data)

        return super().do(action_context, view, impersonate_user, *args, **kwargs)


class SetImpersonateJWTOnCookieAction(JWTCookieActionMixin, ImpersonateBaseAction):
    """ Set the impersonated cookie on the response
        Note: This action should be the last one (it modifies the final
              response)
    """

    def do(self, action_context, view, impersonate_user, *args, **kwargs):
        """Sets the jwt token without calculating"""
        # If not in the argument check on the view
        jwt = action_context.extra_context.get('jwt')
        user = action_context.extra_context.get('user')
        if not jwt:
            logger.error("Not jwt token to set",
                         extra={'request': action_context.request})

            raise ValueError("Not jwt token to set")

        # Get the host for the cookie
        host = self.get_host(action_context.request)

        # Set the response
        action_context.response = jwt_utils.set_jwt_cookie_to_response(
            response=action_context.response,
            cookie_key=settings.JWT_COOKIE_NAME,
            encoded_jwt=jwt,
            expiration_delta_sec=settings.JWT_IMPERSONATE_COOKIE_EXPIRATION_TIME_DELTA,
            domain=host,
            secure=settings.JWT_COOKIE_ONLY_HTTPS)

        logger.info("JWT token set for user {0} on {1}".format(impersonate_user, host))

        logger.info("User '{0}' impersonated user '{1}'".format(
                    user.id,
                    impersonate_user.id))

        return super().do(action_context, view, impersonate_user, *args, **kwargs)

class ImpersonationMetricAction(ImpersonateBaseAction):

    def do(self, action_context, view, impersonate_user, *args, **kwargs):
        inc_impersonations()
        return super().do(action_context, view, impersonate_user, *args, **kwargs)
