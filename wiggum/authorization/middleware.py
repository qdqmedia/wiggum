import logging
import re

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden

logger = logging.getLogger(__name__)


class WiggumValidCloneDomainMiddleware(object):
    """ Check if the wiggum entry domain is valid when clone cookie is active
    """

    def process_request(self, request):
        # Only apply middleware for the required urls
        break_middleware = False
        for i in settings.EXCLUDE_DOMAIN_CHECK_URLS:
            if re.match(i, request.path):
                break_middleware = True

        if break_middleware:
            return None

        # Check clone active
        # and host not in valid clone domain
        # and valid request path
        if not break_middleware and \
            settings.JWT_COOKIE_CLONE and \
            request.META.get('HTTP_HOST') not in \
                settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT:

            logger.warning(
                "Domain '{0}' not valid for jwt cloning".format(
                    request.META.get('HTTP_HOST')))

            # Redirect to the first valid host if is a GET request
            if request.method == "GET":
                valid_host = settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT[0]
                schema = "https://" if settings.JWT_COOKIE_ONLY_HTTPS else "http://"
                url = "".join((schema, valid_host, request.path))
                return HttpResponseRedirect(url)

            # If PUT, POST, PATCH... error code 403 (forbidden)
            return HttpResponseForbidden("Invalid domain")
