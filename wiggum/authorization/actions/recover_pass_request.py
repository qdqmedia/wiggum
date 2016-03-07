import logging
import urllib

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.request import QueryDict
from django.utils.translation import ugettext_lazy as _

from metrics import inc_password_reset_requests
from users.models import User
from users.utils import refresh_password_reset_token
from authorization.utils import get_redirect_url

logger = logging.getLogger(__name__)


class RequestPasswordResetBaseAction(object):
    """Request password reset Base action"""
    def do(self, action_context, view, email, *args, **kwargs):
        return action_context


class LoadUserFromDatabaseAction(RequestPasswordResetBaseAction):
    """ Loads the user from the database
        NOTE: Should be the first action
    """

    def do(self, action_context, view, email, *args, **kwargs):
        users = User.objects.filter(email=email)
        action_context.extra_context['user'] = users[0] if users else None

        return super().do(action_context, view, email, *args, **kwargs)

class CheckUserCorrectAction(RequestPasswordResetBaseAction):
    """Checks if the user is correct and breaks the chain if not"""

    def do(self, action_context, view, email, *args, **kwargs):
        user = action_context.extra_context.get('user')

        if not user:
            msg = _("We haven't found any account with email {0}").format(email)
            messages.add_message(action_context.request, messages.ERROR, msg)
            logger.info(("Recover password not sent to {0} (email not found)"
                ).format(email))

            # Set the initial form with the next value
            uri = get_redirect_url(action_context.request)  # Get the uri from the url first
            if not uri:
                form = action_context.extra_context["form"]
                # Try second time from the form
                uri = form.get_redirect_uri()

            form = view.get_form_class()(initial={
                'redirect_uri': uri})
            action_context.response = view.render_to_response(
                view.get_context_data(form=form))
            action_context.break_chain = True

        return super().do(action_context, view, email, *args, **kwargs)


class CreateRecoverPasswordTokenAction(RequestPasswordResetBaseAction):
    """ Creates the token and the expiration date for the password resetand the URL"""

    def do(self, action_context, view, email, *args, **kwargs):
        # Reset token
        user = action_context.extra_context.get('user')
        if user:
            refresh_password_reset_token(user)
            url = reverse('auth:reset-password', kwargs={
                'user_id': user.id,
                'uuid': str(user.password_reset_token)})

            # Prepare the full url (get the domain from the asked
            # wiggum entrypoint)
            domain = action_context.request.META.get('HTTP_HOST')
            scheme = 'http' if settings.DEBUG else "https"

            # Get redirection uri
            params = QueryDict(mutable=True)
            redirect_uri = action_context.extra_context.get("redirect_uri")
            if redirect_uri:
                params[settings.REDIRECT_URL_VALID_PARAMS[0]] = redirect_uri

            url = urllib.parse.ParseResult(scheme=scheme,
                                           netloc=domain,
                                           path=url,
                                           params="",
                                           query=params.urlencode(),
                                           fragment="").geturl()

            action_context.extra_context['pass_reset_url'] = url
            logger.debug("Password recover url created: {0}".format(url))
        return super().do(action_context, view, email, *args, **kwargs)


class PasswordResetRequestMetricAction(RequestPasswordResetBaseAction):
    def do(self, action_context, view, email, *args, **kwargs):
        inc_password_reset_requests()
        return super().do(action_context, view, email, *args, **kwargs)
