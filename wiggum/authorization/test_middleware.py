from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings
from django.test.client import RequestFactory

from .middleware import WiggumValidCloneDomainMiddleware


@override_settings(
    JWT_COOKIE_CLONE=True,
    JWT_COOKIE_CLONE_DOMAINS_ENDPOINT=(
        "login.test1.com",
        "login.test2.com",
        "login.test3.com",
    ),
)
class WiggumValidCloneDomainMiddlewareTests(TestCase):

    def setUp(self):
        self.start_host = settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT[0]
        self.wiggum_middleware = WiggumValidCloneDomainMiddleware()

    def test_domain_ok(self):
        factory = RequestFactory(HTTP_HOST=self.start_host)
        request = factory.get(reverse("auth:login"))
        response = self.wiggum_middleware.process_request(request)
        self.assertIsNone(response)

    def test_domain_GET_wrong(self):
        factory = RequestFactory(HTTP_HOST="login.test4.com")
        request = factory.get(reverse("auth:login"))
        response = self.wiggum_middleware.process_request(request)
        good_url = "".join(("http://", self.start_host, reverse("auth:login")))

        self.assertIsNotNone(response, good_url)
        self.assertEqual(good_url, response.url)
        self.assertEqual(302, response.status_code)

    @override_settings(
        JWT_COOKIE_CLONE=False
    )
    def test_domain_GET_clone_disabled(self):
        factory = RequestFactory(HTTP_HOST="login.test4.com")
        request = factory.get(reverse("auth:login"))
        response = self.wiggum_middleware.process_request(request)
        self.assertIsNone(response)

    def test_domain_POST_wrong(self):
        factory = RequestFactory(HTTP_HOST="login.test4.com")
        body = {
            'username_or_email': "test",
            'password': "test2",
        }
        request = factory.post(reverse("auth:login"), body)
        response = self.wiggum_middleware.process_request(request)
        self.assertEqual(403, response.status_code)
        self.assertEqual("Invalid domain", response.content.decode())

    def test_domain_wrong_API(self):
        factory = RequestFactory(HTTP_HOST="login.test4.com")
        request = factory.get(reverse("api:user-list"))
        response = self.wiggum_middleware.process_request(request)

        self.assertIsNone(response)
