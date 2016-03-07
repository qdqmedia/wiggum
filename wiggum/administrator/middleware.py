import re

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import login, authenticate, load_backend
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


class JWTAuthMiddleware(object):
    """ Checks if wiggum has authenticated the user with a JWT token on the
        cookie
    """

    def process_request(self, request):
        # Only apply middleware for the required urls
        break_middleware = True
        for i in settings.JWT_SET_DJANGO_SESSION_URLS:
            if re.match(i, request.path):
                break_middleware = False

        if break_middleware:
            return None

        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.
        if request.user.is_authenticated():
            # An authenticated user is associated with the request, but
            # it does not match the jwt user, if it doesn't match
            # the user should be logged to the jwt user. If the users match
            # then we continue
            if request.user.id == self.clean_id(request):
                return

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user. (we pass the request so the jwt auth
        # backend does the hard work)
        user = authenticate(request=request)
        if user:
            # User is valid.  Set request.user and persist user in the session
            # by logging the user in.
            request.user = user
            login(request, user)

    # Method taken from [clean_username]RemoteUserMiddleware
    # (`django/contrib/auth/middleware.py`)
    def clean_id(self, request):
        """
        Allows the backend to clean the user id, if the backend defines a
        clean_id method.
        """
        backend_str = request.session[auth.BACKEND_SESSION_KEY]
        backend = load_backend(backend_str)
        try:
            user_id = backend.clean_id(request)
        except AttributeError:  # Backend has no clean_id method.
            pass
        return user_id


class AdminAuthorizationRedirectMiddleware(object):
    """ This middleware checks the permission of the logged user and redirects
        the user if neccesary
    """

    def process_request(self, request):

        # Only admin pages
        if not request.path.startswith(reverse('admin:index')):
            return None

        if request.user.is_authenticated():
            if not self.shall_pass(request):
                return HttpResponseRedirect(
                    settings.ADMIN_UNATHORIZED_REDIRECTION_URL)

    def shall_pass(self, request):
        return request.user.is_active and request.user.is_staff
