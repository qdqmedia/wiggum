import logging
import uuid
import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone

logger = logging.getLogger(__name__)


def refresh_password_reset_token(user, seconds=None, save=True):
    if not seconds:
        seconds = settings.PASSWORD_RESET_EXPIRE_DELTA

    logger.debug("Token reset request for user".format(user))
    user.password_reset_token = uuid.uuid4()
    now = timezone.now()
    user.password_reset_token_expire = now + datetime.timedelta(
        seconds=seconds)
    if save:
        user.save()


def refresh_sfa_token(user, seconds=None, save=True):
    if not seconds:
        seconds = settings.JWT_SFA_EXPIRE_DELTA

    logger.debug("Token sfa request for user".format(user))
    user.sfa_token = uuid.uuid4()
    now = timezone.now()
    user.sfa_token_expire = now + datetime.timedelta(
        seconds=seconds)
    if save:
        user.save()


def create_password_reset_url(user, expiration_seconds):
    refresh_password_reset_token(user, expiration_seconds)

    # Get url
    return reverse('auth:reset-password', kwargs={
        'user_id': user.id,
        'uuid': str(user.password_reset_token)
    })
