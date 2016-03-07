import uuid
import logging
import re
import urllib.parse

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import FormView
from django.views.generic import TemplateView, RedirectView

from themes.mixins import DynamicTemplateMixin
from users.models import User
from .actions import WiggumActionContext
from .forms import LoginForm, ResetPasswordForm, RecoverPasswordForm
from .utils import str_to_class, create_next_domains_url, get_redirect_url
from . import jwt_utils


logger = logging.getLogger(__name__)


class LoginView(DynamicTemplateMixin, FormView):
    template_name = 'authorization/login.html'
    form_class = LoginForm

    # Default  success
    success_url = settings.LOGIN_SUCCESS_REDIRECT

    # Actions
    pre_check_actions = settings.LOGIN_PRE_CHECK
    success_actions = settings.LOGIN_SUCCESS_ACTIONS
    failure_actions = settings.LOGIN_FAILURE_ACTIONS
    auth_backends = settings.WIGGUM_AUTHENTICATION_BACKENDS

    # Handy information
    user_authenticated = False
    jwt_token = None

    def get_login_pre_check_actions(self):
        return [str_to_class(action)() for action in self.pre_check_actions]

    def get_login_success_actions(self):
        return [str_to_class(action)() for action in self.success_actions]

    def get_login_failure_actions(self):
        return [str_to_class(action)() for action in self.failure_actions]

    def get_authentication_backends(self):
        return [str_to_class(backend)() for backend in self.auth_backends]

    def get(self, request, *args, **kwargs):
        """ Check if there is authenticated already before showing him the
            authentication form
        """
        response = super().get(request, *args, **kwargs)
        extra_context = {
            'redirect_url': self.get_success_url()
        }
        # Start actions
        action_context = WiggumActionContext(request, response, extra_context)
        for action in self.get_login_pre_check_actions():
            action_context = action.do(action_context, self)
            if action_context.break_chain:  # no more action chain to process
                break

        return action_context.response

    def form_valid(self, form):
        # neccessary data to pass to the backends
        credential_data = {
            'username': form.cleaned_data['username_or_email'],
            'password': form.cleaned_data['password'],
            'request': self.request, }

        # Check if user authenticates one backend at a time
        actions_context = {}
        backends = self.get_authentication_backends()
        for i in backends:
            user_authenticated = i.authenticate(**credential_data)
            if user_authenticated:
                actions_context['user_authenticated'] = True
                break

        # If not none then the user is authenticated
        if user_authenticated:
            logger.info("User {0} authenticated".format(user_authenticated))
            # Redirect to asked url if present, if not, default
            if form.get_redirect_uri():
                self.success_url = form.get_redirect_uri()

            response = super().form_valid(form)

            # Start loggin success actions (create token, set on cookie...)
            action_context = WiggumActionContext(self.request,
                                                 response,
                                                 actions_context)
            for action in self.get_login_success_actions():
                action_context = action.do(action_context,
                                           self,
                                           user_authenticated)
                if action_context.break_chain:  # no more action chain to process
                    break

            return action_context.response

        # Reset password and username but not the redirect_uri
        form = self.get_form_class()(initial={
            'redirect_uri': form.get_redirect_uri()})
        response = self.render_to_response(self.get_context_data(form=form))

        # Start failure actions
        action_context = WiggumActionContext(self.request,
                                             response,
                                             actions_context)
        for action in self.get_login_failure_actions():
            action_context = action.do(action_context,
                                       self,
                                       user_authenticated)
            if action_context.break_chain:  # no more action chain to process
                break

        # DONT DO THIS AT HOME KIDS!
        # Small and ugly hack for sentry password deletion (ugly... but that's
        # life when you cant do a deep copy of an object easily).
        mutable = self.request.POST._mutable
        self.request.POST._mutable = True
        password = self.request.POST['password']
        self.request.POST['password'] = '************'
        body = getattr(self.request, "_body", b"")
        self.request._body = re.sub("(password=)[^&]*(.*|$)",
                                    "\g<1>************\g<2>",
                                    body.decode("utf-8")).encode()

        logger.warning("User authentication failed",
                       extra={'request': self.request, 'response': response})

        self.request.POST['password'] = password
        self.request.POST._mutable = mutable
        setattr(self.request, "_body", body)
        return action_context.response

    def get_success_url(self):
        uri = get_redirect_url(self.request)

        if not uri:
            return super().get_success_url()
        return uri


    def get_initial(self):
        # Set the return url as a hidden field on the form
        initial = super().get_initial()

        uri = self.get_success_url()
        if uri:
            try:
                URLValidator(uri)
                initial['redirect_uri'] = uri
            except ValidationError:  # If not an url, set default one
                initial['redirect_uri'] = self.success_url
        return initial


class RecoverPasswordView(DynamicTemplateMixin, FormView):
    """Creates the token and sends the email"""

    template_name = 'authorization/recover_password.html'
    form_class = RecoverPasswordForm
    user = None

    # Default  success
    success_url = settings.RECOVER_PASS_REQUEST_SUCCESS_REDIRECT

    # Actions
    recover_actions = settings.RECOVER_PASS_REQUEST_ACTIONS

    def get_recover_actions(self):
        return [str_to_class(action)() for action in self.recover_actions]

    def form_valid(self, form):
        response = super().form_valid(form)
        email = form.cleaned_data['email']
        extra_context = {
            "redirect_uri": form.get_redirect_uri(),
            "form": form,
        }

        # Do recover password actions (send email...)
        action_context = WiggumActionContext(self.request,
                                             response,
                                             extra_context)
        for action in self.get_recover_actions():
            action_context = action.do(action_context, self, email)
            if action_context.break_chain:  # no more action chain to process
                break

        return action_context.response

    def get_initial(self):
        # Set the return url as a hidden field on the form
        initial = super().get_initial()

        uri = get_redirect_url(self.request)
        if uri:
            try:
                URLValidator(uri)
                initial['redirect_uri'] = uri
            except ValidationError:  # If not an url, set default one
                initial['redirect_uri'] = self.success_url
        return initial

class ResetPasswordView(DynamicTemplateMixin, FormView):
    template_name = 'authorization/reset_password.html'
    form_class = ResetPasswordForm

    # Default  success
    success_url = settings.RESET_PASS_SUCCESS_REDIRECT

    reset_pass_actions = settings.RESET_PASS_ACTIONS

    def get_reset_pass_actions(self):
        return [str_to_class(action)() for action in self.reset_pass_actions]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uuid'] = self.kwargs['uuid']
        context['user_id'] = self.kwargs['user_id']
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        # Check token and expiration
        try:
            user = User.objects.get(id=self.kwargs['user_id'])
            if str(user.password_reset_token) == self.kwargs['uuid']:
                if user.password_reset_token_expire <= timezone.now():
                    logger.info(
                        "password reset for user {0} token has expire".format(
                            user))
                    msg = _("Token for password reset expired")
                    messages.add_message(self.request, messages.ERROR, msg)
                    return response
                else:  # All ok, reset password
                    # Reset token
                    user.password_reset_token = uuid.uuid4()
                    # Set password
                    user.set_password(form.cleaned_data['password'])
                    # Set user as migrated
                    user.external_service = ""
                    user.save()
                    logger.info(
                        "Password for user {0} has been reset".format(user))
                    msg = _("Password has been reset")
                    messages.add_message(self.request, messages.SUCCESS, msg)

                    # We know that the user access the email(?),
                    # we trust the user
                    action_context = {
                        'user_authenticated': True,
                    }

                    # Redirect to asked url if present, if not, default
                    if form.get_redirect_uri() and form.get_redirect_uri():
                        self.success_url = form.get_redirect_uri()

                    # Do password reset actions
                    action_context = WiggumActionContext(self.request,
                                                         response,
                                                         action_context)
                    for action in self.get_reset_pass_actions():
                        action_context = action.do(action_context, self, user)
                        if action_context.break_chain:  # no more action chain to process
                            break

                    return action_context.response

            logger.info("Password reset denied for user {0}".format(user))
        except User.DoesNotExist:
            pass  # Dont give hits of non existent user
            logger.info("Password reset denied")
        # Dont reset password, token not valid
        msg = _("Password reset denied")
        messages.add_message(self.request, messages.ERROR, msg)
        return response

    def get_initial(self):
        # Set the return url as a hidden field on the form
        initial = super().get_initial()

        uri = get_redirect_url(self.request)
        if uri:
            try:
                URLValidator(uri)
                initial['redirect_uri'] = uri
            except ValidationError:  # If not an url, set default one
                initial['redirect_uri'] = self.success_url
        return initial


class JWTTesView(DynamicTemplateMixin, TemplateView):
    """Handy view to test jwt session"""
    template_name = 'authorization/test_jwt.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        jwt = self.request.COOKIES.get(settings.JWT_COOKIE_NAME, None)
        if jwt:
            context['permissions_set'] = settings.JWT_SET_PERMISSION_ON_TOKEN
            context['jwt'] = jwt
            context['jwt_payload'] = jwt_utils.decode_jwt(jwt)
            context['jwt_valid'] = jwt_utils.validate_jwt_all_keys(jwt)

        return context


class CloneCookieView(RedirectView):
    """ Will set the received jwt cookie as a new cookie on this (request)
        domain and redirect
    """

    success_url = settings.CLONE_SUCCESS_REDIRECT
    permanent = False

    # Actions
    clone_actions = settings.CLONE_ACTIONS

    def get_clone_actions(self):
        return [str_to_class(action)() for action in self.clone_actions]

    def get_redirect_url(self, *args, **kwargs):
        url = None
        if settings.JWT_COOKIE_CLONE:
            # Get the token and verify that is a valid token
            jwt_token = self.kwargs.get('token', None)
            if jwt_token and jwt_utils.validate_jwt_all_keys(jwt_token):
                # Get the clone urls
                clone_domains = self.request.GET.getlist("clone-domains", None)

                if clone_domains:
                    # Get next one and create the url
                    if type(clone_domains) == list:
                        next_domain = clone_domains.pop(0)
                    else:
                        next_domain = clone_domains
                        clone_domains = None

                    url_path = urllib.parse.urljoin(next_domain, reverse(
                        'auth:clone-cookie', kwargs={'token': jwt_token}))

                    uri = get_redirect_url(self.request)

                    params = {
                        settings.REDIRECT_URL_VALID_PARAMS[0]: uri}

                    return create_next_domains_url(
                        path=url_path,
                        scheme='http' if settings.DEBUG else "https",
                        domain=next_domain,
                        query_params=params,
                        clone_domains=clone_domains)

            # Redirect to the final uri
            url = get_redirect_url(self.request)

        # Default one
        if not url:
            url = self.success_url

        return url

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        actions_context = {
            'jwt': self.kwargs.get('token', None)
        }

        # Do clone actions (clone the cookie on the domains)
        action_context = WiggumActionContext(self.request,
                                             response,
                                             actions_context)
        for action in self.get_clone_actions():
            action_context = action.do(action_context, self)
            if action_context.break_chain:  # no more action chain to process
                break
        return action_context.response



class LogoutView(RedirectView):
    """ Will unset the cookie on all the domains
    """

    permanent = False

    # Default  success
    success_url = settings.LOGOUT_SUCCESS_REDIRECT

    # Actions
    logout_actions = settings.LOGOUT_ACTIONS

    def get_logout_actions(self):
        return [str_to_class(action)() for action in self.logout_actions]

    def get_redirect_url(self, *args, **kwargs):
        clone_domains = self.request.GET.getlist("clone-domains", None)
        final = self.request.GET.get("final", None)
        redirect_uri = get_redirect_url(self.request)
        url = None

        # If not cloned urls then dont do redirection chain
        if not settings.JWT_COOKIE_CLONE:
            if not redirect_uri:
                redirect_uri = self.success_url
            return redirect_uri

        # If last one then redirect
        if final:
            url = redirect_uri
        else:
            # if not final and not clone domains we start the jwt declone!
            if not clone_domains:
                clone_domains = list(
                    settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT)
                try:
                    clone_domains.remove(self.request.META.get('HTTP_HOST'))
                except ValueError:
                    # Maybe the domain is not on clone domains list but is a
                    # valid wiggum domain, if not then raise an exception
                    if self.request.META.get('HTTP_HOST') not in\
                       settings.ALLOWED_HOSTS:
                        logger.error("Not a valid wiggum domain",
                                     extra={'request': self.request})
                        raise ValueError("Not a valid wiggum domain")
            # Get next domain from clone domains and remove this from the list
            next_domain = clone_domains.pop(0)
            url_path = reverse('auth:logout')
            params = {}

            if redirect_uri:
                params[settings.REDIRECT_URL_VALID_PARAMS[0]] = redirect_uri

            # Set final if no more clone domains
            if len(clone_domains) == 0:
                params['final'] = 1

            # Generate the url
            url = create_next_domains_url(
                path=url_path,
                scheme='http' if settings.DEBUG else "https",
                domain=next_domain,
                query_params=params,
                clone_domains=clone_domains)
        # By default send to "success_url"
        if not url:
            url = self.success_url

        return url

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        # Is the final logout?
        extra_context = {
            'final_logout': True
        }
        if settings.JWT_COOKIE_CLONE and not self.request.GET.get("final", None):
            extra_context['final_logout'] = False

        # Start failure actions
        action_context = WiggumActionContext(self.request,
                                             response,
                                             extra_context)
        for action in self.get_logout_actions():
            action_context = action.do(action_context, self)
            if action_context.break_chain:  # no more action chain to process
                break
        return action_context.response


class ImpersonateView(RedirectView):
    """ Will set an impersonate cookie
    """

    permanent = False

    # Default  success
    success_url = settings.IMPERSONATE_SUCCESS_REDIRECT

    # Actions
    impersonate_actions = settings.IMPERSONATE_ACTIONS

    def get_impersonate_actions(self):
        return [str_to_class(action)() for action in self.impersonate_actions]

    def get_redirect_url(self, *args, **kwargs):
        return self.success_url

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        try:
            user = User.objects.get(id=self.kwargs['user_id'])
            extra_context ={
                'redirect_url': self.get_redirect_url()
            }
            # Start impersonalion actions
            action_context = WiggumActionContext(self.request,
                                                 response,
                                                 extra_context)
            for action in self.get_impersonate_actions():
                action_context = action.do(action_context, self, user)
                if action_context.break_chain:  # no more action chain to process
                    break

            return action_context.response

        except User.DoesNotExist:
            logger.warning("Impersonate user doesn't exists")
            messages.add_message(
                request,
                messages.ERROR,
                _("Invalid user for impersonation"))
        return response


class SFAView(RedirectView):
    """ Will set JWT on cookie """

    permanent = False

    # Default  success
    success_url = settings.SFA_SUCCESS_REDIRECT

    # Actions
    sfa_actions = settings.SFA_ACTIONS

    def get_sfa_actions(self):
        return [str_to_class(action)() for action in self.sfa_actions]

    def get_redirect_url(self, *args, **kwargs):
        return self.success_url

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        try:
            user = User.objects.get(id=self.kwargs['user_id'])
            if str(user.sfa_token) == self.kwargs['uuid']:
                if user.sfa_token_expire <= timezone.now():
                    logger.info(
                        "SFA link  for user '{0}' expired".format(user))
                    msg = _("SFA link expired")
                    messages.add_message(self.request, messages.ERROR, msg)
                    return response
                else:
                    extra_context ={
                        'redirect_url': self.get_redirect_url(),
                        'user_authenticated': True,
                    }
                    # Start SFA actions
                    action_context = WiggumActionContext(self.request,
                                                         response,
                                                         extra_context)
                    for action in self.get_sfa_actions():
                        action_context = action.do(action_context, self, user)
                        if action_context.break_chain:  # no more action chain to process
                            break

                    return action_context.response
            else:
                logger.info(
                    "SFA link  for user '{0}' already used".format(user))
                messages.add_message(
                    request,
                    messages.ERROR,
                    _("Invalid SFA token"))
        except User.DoesNotExist:
            logger.warning("SFA invalid user to login")
            messages.add_message(
                request,
                messages.ERROR,
                _("Invalid user to login"))
        return response
