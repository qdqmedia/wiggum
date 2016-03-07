import urllib.parse

from django.conf import settings
from django.http.request import QueryDict


def str_to_class(string_class):
    module_and_class = string_class.rsplit(".", 1)
    mod = __import__(module_and_class[0], fromlist=[module_and_class[1]])
    return getattr(mod, module_and_class[1])


def create_next_domains_url(path, scheme="http", domain="", query_params={},
                            clone_domains=()):
    """ handy function to create an url with clone domains querystring"""

    # Set the correct params (clones and redirect url)
    # Small hack to create automatically the url :P
    params = QueryDict(mutable=True)
    for k, v in query_params.items():
        params[k] = v

    if len(clone_domains) > 0:
        params.setlist('clone-domains', clone_domains)

    url = urllib.parse.ParseResult(
        scheme=scheme,
        netloc=domain,
        path=path,
        params="",
        query=params.urlencode(),
        fragment="", )

    return url.geturl()


def get_redirect_url(request):
    uri = None
    for i in settings.REDIRECT_URL_VALID_PARAMS:
        uri = request.GET.get(i, None)
        if uri and uri != str(None):
            return uri
