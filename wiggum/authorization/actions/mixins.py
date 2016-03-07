import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class JWTCookieActionMixin(object):
    """Class helper for cookie based actions"""

    def get_host(self, request):
        http_host = request.META.get('HTTP_HOST', settings.JWT_COOKIE_DOMAIN)
        if settings.JWT_COOKIE_DOMAIN_AUTO:
            # For our purpouses this is safe in case of spoofed headers
            # Delete the port
            http_host = http_host.split(":")[0]

            http_host_spl = http_host.split(".")
            # If wrong configuration then set the header one
            if settings.JWT_COOKIE_DOMAIN_AUTO_LEVEL > len(http_host_spl) or\
               settings.JWT_COOKIE_DOMAIN_AUTO_LEVEL <= 1:
                host = http_host
            else:
                h = http_host_spl[-settings.JWT_COOKIE_DOMAIN_AUTO_LEVEL:]
                host = ".{0}".format(".".join(h))
            return host
        return http_host
