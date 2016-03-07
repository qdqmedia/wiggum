from django.conf import settings
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

from .backends import JWTAuthBackend
from authorization import jwt_utils
from users.models import User


@override_settings(
    JWT_SECRET_KEY="test1",
    JWT_VERIFICATION_KEY="test1",
    JWT_SIGN_ALGORITHM="HS256",
    JWT_SIGN_VALID_ALGORITHMS=("HS256",)
)
class JWTAuthBackendTests(TestCase):
    def setUp(self):
        self.user = User()
        self.user.username = "batman"
        self.user.email = "batman@darkknight.com"
        self.user.first_name = "Bruce"
        self.user.last_name = "Wayne"
        self.user.save()

        self.backend = JWTAuthBackend()

        self.jwt_ok = jwt_utils.create_jwt(self.user)
        self.jwt_wrong = jwt_utils.create_jwt(self.user, secret="wrong_key")

    def test_jwt_ok(self):
        request = RequestFactory().get("/something")
        request.COOKIES[settings.JWT_COOKIE_NAME] = self.jwt_ok

        result = self.backend.authenticate(request)

        self.assertEqual(self.user, result)

    def test_bad_jwt(self):
        request = RequestFactory().get("/something")
        request.COOKIES[settings.JWT_COOKIE_NAME] = self.jwt_wrong

        result = self.backend.authenticate(request)

        self.assertIsNone(result)
