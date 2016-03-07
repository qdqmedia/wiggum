import logging

import jwt
import datetime

from django.conf import settings
from django.utils import timezone


logger = logging.getLogger(__name__)


# ----------------------------------------------- #
# Note: all jwt time is in UNIX timestamp (EPOCH) #
# ----------------------------------------------- #


def create_jwt_payload(user, expiration_delta, issuer, version=None, **kwargs):
    timezone.activate(settings.TIME_ZONE)
    now = timezone.now()
    expiration_date = now + datetime.timedelta(seconds=expiration_delta)
    version = settings.JWT_VERSION if not version else version
    not_before = now - datetime.timedelta(
        seconds=settings.JWT_NBF_LEEWAY_SECONDS)

    payload = {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
        # used jwt RFC claims
        # JWT expiration
        "exp": int(expiration_date.strftime("%s")),
        # Issuer of the token
        "iss": issuer,
        # Issued at
        "iat": int(now.strftime("%s")),
        # # Not before (dont use before)
        "nbf": int(not_before.strftime("%s")),
        # # Subject of the token
        # "sub":
        # # Audience of the token
        # "aud":
        # # JWT token id
        # "jti":
        # Version of the token
        "version": version,
    }

    # Only set the permissions on the jwt token if forcen on settings
    if settings.JWT_SET_PERMISSION_ON_TOKEN:
        payload["permission"] = list(
            user.project_permissions.values_list('key', flat=True))

    # Set extra args
    for k, v in kwargs.items():
        payload[k] = v

    return payload


def create_jwt(user, secret=None, algorithm=None, expiration_time=None,
               extra_data={}):

    if not secret:
        secret = settings.JWT_SECRET_KEY
    if not algorithm:
        algorithm = settings.JWT_SIGN_ALGORITHM
    if not expiration_time:
        expiration_time = settings.JWT_EXPIRATION_TIME_DELTA

    payload = create_jwt_payload(user=user,
                                 expiration_delta=expiration_time,
                                 issuer=settings.JWT_ISSUER,
                                 **extra_data)

    return jwt.encode(payload, secret, algorithm=algorithm)


def set_jwt_cookie_to_response(response, encoded_jwt, cookie_key,
                               expiration_delta_sec, domain, secure):
    """ Sets the jwt token on the received response"""
    # Set the cookie with jwt
    #   * We set max_age and not expire
    #   * Domain set ensures cookie subdomain availability
    #   * Path to / (default) ensures all the domain
    response.set_cookie(key=cookie_key,
                        value=encoded_jwt,
                        max_age=expiration_delta_sec,
                        domain=domain,
                        secure=secure)

    return response


def valid_jwt(encoded_jwt, secret, algorithms=[]):
    if not algorithms:
        algorithms = []
    try:
        jwt.decode(encoded_jwt, secret, algorithms=algorithms)
        return True
    except (jwt.InvalidTokenError, jwt.exceptions.InvalidKeyError,
            TypeError, ValueError, AttributeError) as e:
        logger.warning("Invalid JWT token", extra={
            'exception': str(e),
            'jwt_token': encoded_jwt})
        return False


def validate_jwt_all_keys(encoded_jwt):
    """Validate the jwt token with all the keys"""

    keys_to_check = (
        settings.JWT_VERIFICATION_KEY,
    )

    if settings.JWT_TRANSITION_ENABLE:
        keys_to_check += (settings.JWT_TRANSITION_VERIFICATION_KEY, )

    # Check all the keys until one is valid
    for i in keys_to_check:
        if valid_jwt(encoded_jwt, i, settings.JWT_SIGN_VALID_ALGORITHMS):
            return True

    return False


def decode_jwt(encoded_jwt):
    """Returns decoded jwt """
    return jwt.decode(encoded_jwt, verify=False)
