import time

from django.conf import settings
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings


from users.models import User
from .backends import RegularDatabaseAuthentication, JWTAuthentication
from . import jwt_utils


class RegularDatabaseAuthenticationBackendTests(TestCase):

    def setUp(self):
        self.user = User(username="dark-knight4",
                         email="brucewayne@batman.com",
                         first_name="Bruce",
                         last_name="Wayne")
        self.user.save()
        self.user_password = "dark_knight_password"
        self.user.set_password(self.user_password)
        self.user.save()

    def test_auth_username_ok(self):
        backend = RegularDatabaseAuthentication()
        u = backend.authenticate(username=self.user.username,
                                 password=self.user_password)

        self.assertEqual(self.user, u)

    def test_auth_email_ok(self):
        backend = RegularDatabaseAuthentication()
        u = backend.authenticate(username=self.user.email,
                                 password=self.user_password)

        self.assertEqual(self.user, u)

    def test_auth_wrong(self):
        backend = RegularDatabaseAuthentication()
        u = backend.authenticate(username=self.user.username,
                                 password="wrong")

        self.assertIsNone(u)

    def test_auth_not_active_wrong(self):
        self.user.active = False
        self.user.save()
        backend = RegularDatabaseAuthentication()
        u = backend.authenticate(username=self.user.username,
                                 password=self.user_password)

        self.assertIsNone(u)

class JWTAuthenticationBackendTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User(username="dark-knight4",
                         email="brucewayne@batman.com",
                         first_name="Bruce",
                         last_name="Wayne")
        self.user.save()
        self.user_password = "dark_knight_password"
        self.user.set_password(self.user_password)
        self.user.save()

    def test_auth_ok(self):
        backend = JWTAuthentication()
        encoded_jwt = jwt_utils.create_jwt(self.user)
        request = self.factory.get('')
        request.COOKIES[settings.JWT_COOKIE_NAME] = encoded_jwt

        u = backend.authenticate(request=request)

        self.assertEqual(self.user, u)

    @override_settings(JWT_EXPIRATION_TIME_DELTA=(1*settings.SECOND))
    def test_expired(self):
        backend = JWTAuthentication()
        encoded_jwt = jwt_utils.create_jwt(self.user)
        request = self.factory.get('')
        request.COOKIES[settings.JWT_COOKIE_NAME] = encoded_jwt

        time.sleep(2*settings.SECOND)
        u = backend.authenticate(request=request)

        self.assertIsNone(u)

    def test_wrong_jwt(self):
        backend = JWTAuthentication()
        encoded_jwt = jwt_utils.create_jwt(self.user)
        encoded_jwt = encoded_jwt[:-3] + b'abc'
        request = self.factory.get('')
        request.COOKIES[settings.JWT_COOKIE_NAME] = encoded_jwt

        u = backend.authenticate(request=request)

        self.assertIsNone(u)

    def test_wrong_user_id(self):
        backend = JWTAuthentication()
        self.user.id = 9999
        encoded_jwt = jwt_utils.create_jwt(self.user)
        request = self.factory.get('')
        request.COOKIES[settings.JWT_COOKIE_NAME] = encoded_jwt

        u = backend.authenticate(request=request)

        self.assertIsNone(u)
