from django.conf import settings
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore

from .middleware import AdminAuthorizationRedirectMiddleware, JWTAuthMiddleware
from authorization import jwt_utils
from users.models import User


class AdminAuthorizationRedirectMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = AdminAuthorizationRedirectMiddleware()

        self.user = User()
        self.user.username = "batman"
        self.user.email = "batman@darkknight.com"
        self.user.first_name = "Bruce"
        self.user.last_name = "Wayne"
        self.user.save()

    def test_not_admin_url(self):
        request = RequestFactory().get("/something")
        result = self.middleware.process_request(request)

        self.assertIsNone(result)

    def test_admin_url_user_not_staff(self):
        request = RequestFactory().get(reverse("admin:index"))
        request.user = self.user
        result = self.middleware.process_request(request)

        self.assertEqual(settings.ADMIN_UNATHORIZED_REDIRECTION_URL, result.url)
        self.assertTrue(isinstance(result, HttpResponseRedirect))

    def test_admin_url_user_staff(self):
        adm = User.objects.create_superuser(username="batmanadmin",
                                            email="batman@admin.com")
        request = RequestFactory().get(reverse("admin:index"))
        request.user = adm
        result = self.middleware.process_request(request)

        self.assertIsNone(result)

@override_settings(
    JWT_SET_DJANGO_SESSION_URLS=(
        "/middleware",
    ),
    JWT_SECRET_KEY="test1",
    JWT_VERIFICATION_KEY="test1",
    JWT_SIGN_ALGORITHM="HS256",
    JWT_SIGN_VALID_ALGORITHMS=("HS256",)
)
class JWTAuthMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = JWTAuthMiddleware()

        self.user = User()
        self.user.username = "batman"
        self.user.email = "batman@darkknight.com"
        self.user.first_name = "Bruce"
        self.user.last_name = "Wayne"
        self.user.save()

        self.jwt = jwt_utils.create_jwt(self.user)

    def test_not_jwt(self):
        request = RequestFactory().get("/middleware")
        # Set no session request
        anon = AnonymousUser()
        request.user = anon
        request.session = SessionStore()

        result = self.middleware.process_request(request)
        self.assertIsNone(result)
        self.assertEqual(anon, request.user)

    def test_jwt(self):
        request = RequestFactory().get("/middleware")
        # Set no session
        anon = AnonymousUser()
        request.user = anon
        request.session = SessionStore()

        # Set the jwt COOKIES
        request.COOKIES[settings.JWT_COOKIE_NAME] = self.jwt

        result = self.middleware.process_request(request)
        self.assertIsNone(result)
        self.assertEqual(self.user, request.user)
        self.assertEqual(self.user.id, int(request.session.get('_auth_user_id')))
        self.assertEqual("administrator.backends.JWTAuthBackend",
                         request.session.get('_auth_user_backend'))

    @override_settings(
        JWT_SET_DJANGO_SESSION_URLS=(
            "/notsomething",
        )
    )
    def test_not_aplicable_url(self):
        # Without anon user (or user) should fail if enters the appplicable url
        # flow
        with self.assertRaises(AttributeError):
            request = RequestFactory().get("/notsomething")
            result = self.middleware.process_request(request)

        request = RequestFactory().get("/something")
        result = self.middleware.process_request(request)
        self.assertIsNone(result)
