import logging

import uuid

from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class SFABaseAction(object):
    """SFA base action"""
    def do(self, action_context, view, user, *args, **kwargs):
        return action_context


class CheckSFAActiveAction(SFABaseAction):
    """Checks if SFA feature is active"""

    def do(self, action_context, view, user, *args, **kwargs):
        if not settings.JWT_SFA_ENABLE:
            action_context.break_chain = True

            # Add an error message
            messages.add_message(action_context.request, messages.ERROR,
                                 _("SFA not active"))

        return super().do(action_context, view, user, *args, **kwargs)


class ResetSFATokenAction(SFABaseAction):
    """Resets the SFA token"""

    def do(self, action_context, view, user, *args, **kwargs):
        # Reset token (one use token)
        user.sfa_token = uuid.uuid4()
        user.save()

        logger.info(
            "SFA token used for user '{0}', resetting...".format(user.username))

        return super().do(action_context, view, user, *args, **kwargs)
