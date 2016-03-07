import logging

from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from . import jwt_utils
from users.models import User

logger = logging.getLogger(__name__)


class BaseAuthentication(object):
    """ Base authentication class.
        In order to implement authentication, should extend this class and
        implement authenticate method receiving first parameters (user,
        password, token, cookie...)
        If authentication is ok, should return an object
        (user, list...) None if not authenticated
    """

    def authenticate(self, **kwargs):
        raise NotImplementedError("Base class")


class RegularDatabaseAuthentication(BaseAuthentication):
    """ Basic authentication based on database lookup """

    def authenticate(self, username=None, password=None, *args, **kwargs):
        """ Authenticates an user, returns the user if correct, None instead
        """
        # First check we required data
        if username and password:
            try:
                # Check if email or username
                try:
                    validate_email(username)
                    u = User.objects.get(email=username)
                except ValidationError:
                    u = User.objects.get(username=username)
                if u.check_password(password) and u.active:
                    # Update the last time that was logged
                    u.last_login = timezone.now()
                    u.save(update_fields=['last_login'])
                    return u
            except User.DoesNotExist:
                pass

        # No luck, try it next time unathenticated user!
        return None


class JWTAuthentication(BaseAuthentication):
    """ Checks if the user is authenticated already with a jwt token """

    def authenticate(self, request, *args, **kwargs):
        """ Authenticates an user, returns the user if correct, None instead
        """

        jwt = request.COOKIES.get(settings.JWT_COOKIE_NAME, None)
        if jwt:
            if jwt_utils.validate_jwt_all_keys(jwt):
                try:
                    user_id = jwt_utils.decode_jwt(jwt)['user']['id']
                    user = User.objects.get(id=user_id)
                    return user
                except User.DoesNotExist:
                    pass
        return None
