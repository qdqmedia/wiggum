import datetime
import urllib.parse
import uuid
import time

from django.core.urlresolvers import reverse
from django.http.request import QueryDict
from django.conf import settings
from django.test import TestCase, Client
from django.test.utils import override_settings
from django.utils import timezone
import jwt

from users.models import User, ProjectPermission
from users.utils import refresh_sfa_token
from . import jwt_utils


class LoginTests(TestCase):

    def setUp(self):
        self.login_url = reverse("auth:login")
        self.user = User(username="dark-knight4",
                         email="brucewayne@batman.com",
                         first_name="Bruce",
                         last_name="Wayne")
        self.user.save()
        self.user_password = "dark_knight_password"
        self.user.set_password(self.user_password)
        self.user.save()
    @override_settings(
        JWT_COOKIE_CLONE=False
    )
    def test_login_user_email(self):
        body = {
            'username_or_email': self.user.email,
            'password': self.user_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check
        theme_template = "{0}/authorization/test_jwt.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])
        self.assertEqual(1, len(resp.redirect_chain))
        self.assertEqual(("http://testserver/a/test/jwt", 302), resp.redirect_chain[0])
        self.assertEqual(200, resp.status_code)

    @override_settings(
        JWT_COOKIE_CLONE=False
    )
    def test_login_user_username(self):
        body = {
            'username_or_email': self.user.username,
            'password': self.user_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check
        theme_template = "{0}/authorization/test_jwt.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])
        self.assertEqual(1, len(resp.redirect_chain))
        self.assertEqual(("http://testserver/a/test/jwt", 302), resp.redirect_chain[0])
        self.assertEqual(200, resp.status_code)

    @override_settings(
        JWT_COOKIE_CLONE=False
    )
    def test_login_redirect(self):
        body = {
            'username_or_email': self.user.username,
            'password': self.user_password,
            'redirect_uri': "http://google.com",
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check
        self.assertEqual(1, len(resp.redirect_chain))
        self.assertEqual(("http://google.com", 302), resp.redirect_chain[0])

    @override_settings(
        JWT_COOKIE_CLONE=False,
        FORCE_LOGIN_FORM=False
    )
    def test_already_loged_redirect_default(self):
        body = {
            'username_or_email': self.user.username,
            'password': self.user_password,
            'redirect_uri': "http://google.com",
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check first login
        self.assertEqual(1, len(resp.redirect_chain))
        self.assertEqual(("http://google.com", 302), resp.redirect_chain[0])

        # Check redirect
        resp = self.client.get(self.login_url, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertTrue(settings.LOGIN_SUCCESS_REDIRECT in
                        resp.redirect_chain[0][0])
    @override_settings(
        JWT_COOKIE_CLONE=False,
        FORCE_LOGIN_FORM=False
    )
    def test_already_loged_redirect_custom(self):
        body = {
            'username_or_email': self.user.username,
            'password': self.user_password,
            'redirect_uri': "http://google.com",
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check first login
        self.assertEqual(1, len(resp.redirect_chain))
        self.assertEqual(("http://google.com", 302), resp.redirect_chain[0])

        # Check redirect
        redirect_uri = "http://google2.com"
        redirect_param = settings.REDIRECT_URL_VALID_PARAMS[0]
        url = "{0}?{1}={2}".format(self.login_url, redirect_param, redirect_uri)
        resp = self.client.get(url, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(redirect_uri, resp.redirect_chain[0][0])

    def test_login_user_wrong(self):
        body = {
            'username_or_email': self.user.email,
            'password': "wrong_password",
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check
        theme_template = "{0}/authorization/login.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])
        self.assertEqual(0, len(resp.redirect_chain))
        self.assertEqual(200, resp.status_code)
        messages = list(resp.context['messages'])
        self.assertEqual(1, len(messages))
        self.assertEqual("Authentication error", messages[0].message)

    def test_login_user_not_active(self):
        self.user.active = False
        self.user.save()

        body = {
            'username_or_email': self.user.email,
            'password': self.user_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check
        theme_template = "{0}/authorization/login.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])
        self.assertEqual(0, len(resp.redirect_chain))
        self.assertEqual(200, resp.status_code)
        messages = list(resp.context['messages'])
        self.assertEqual(1, len(messages))
        self.assertEqual("Authentication error", messages[0].message)

    @override_settings(
        JWT_VERSION=99,
        JWT_COOKIE_CLONE=False,
        JWT_COOKIE_DOMAIN="127.0.0.1",
        JWT_COOKIE_DOMAIN_AUTO=False)
    def test_login_jwt_cookie(self):
        body = {
            'username_or_email': self.user.email,
            'password': self.user_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check
        self.assertEqual(200, resp.status_code)

        # Check cookie ok
        jwt_cookie = self.client.cookies[settings.JWT_COOKIE_NAME]
        self.assertEqual(settings.JWT_COOKIE_DOMAIN, jwt_cookie['domain'])
        self.assertEqual("/", jwt_cookie['path'])
        self.assertEqual(settings.JWT_COOKIE_EXPIRATION_TIME_DELTA,
                         jwt_cookie['max-age'])

        # Check if the jwt is valid (if not valid, decode should
        # throw an exception)
        jwt_encoded = jwt_cookie.value
        jwt_decoded = jwt.decode(jwt_encoded,
                                 settings.JWT_SECRET_KEY,
                                 [settings.JWT_SIGN_ALGORITHM, ])

        # Check jwt content ok
        for k, v in jwt_decoded['user'].items():
            self.assertEqual(getattr(self.user, k), v)

        # Check permission
        for k, i in enumerate(self.user.project_permissions.all()):
            self.assertEqual(i.key, jwt_decoded['permission'][k])

        # Check version
        self.assertEqual(settings.JWT_VERSION,
                         float(jwt_decoded['version']))

    @override_settings(
        JWT_VERSION=99,
        JWT_COOKIE_CLONE=False,
        JWT_COOKIE_DOMAIN="127.0.0.1",
        JWT_COOKIE_DOMAIN_AUTO=False,
        JWT_SECRET_KEY="test1",
        JWT_SIGN_ALGORITHM="HS256")
    def test_login_transition_jwt_cookie(self):
        # Login and get the jwt cookie
        body = {
            'username_or_email': self.user.email,
            'password': self.user_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check
        self.assertEqual(200, resp.status_code)

        # Check cookie ok
        jwt_cookie = self.client.cookies[settings.JWT_COOKIE_NAME]
        self.assertEqual(settings.JWT_COOKIE_DOMAIN, jwt_cookie['domain'])

        # Change settings to deprecate the key
        with self.settings(
            JWT_SECRET_KEY="newtest1",
            JWT_SIGN_ALGORITHM="HS256",
            JWT_TRANSITION_ENABLE=True,
            JWT_TRANSITION_VERIFICATION_KEY="test1",
            JWT_SIGN_VALID_ALGORITHMS=("HS256",)):

            resp = self.client.get(self.login_url, follow=True)
            self.assertEqual(200, resp.status_code)
            self.assertTrue(settings.LOGIN_SUCCESS_REDIRECT in
                            resp.redirect_chain[0][0])


    @override_settings(
        JWT_VERSION=99,
        JWT_COOKIE_CLONE=False,
        JWT_COOKIE_DOMAIN="127.0.0.1",
        JWT_COOKIE_DOMAIN_AUTO=False,
        JWT_SECRET_KEY="test1",
        JWT_SIGN_VALID_ALGORITHMS=("HS256",))
    def test_login_transition_jwt_cookie_wrong(self):
        # Login and get the jwt cookie
        body = {
            'username_or_email': self.user.email,
            'password': self.user_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check
        self.assertEqual(200, resp.status_code)

        # Check cookie ok
        jwt_cookie = self.client.cookies[settings.JWT_COOKIE_NAME]
        self.assertEqual(settings.JWT_COOKIE_DOMAIN, jwt_cookie['domain'])

        # Change settings to invalidate the key
        with self.settings(
            JWT_SECRET_KEY="newtest1",
            JWT_SIGN_ALGORITHM="HS256",
            JWT_TRANSITION_ENABLE=True,
            JWT_TRANSITION_VERIFICATION_KEY="test2",
            JWT_SIGN_VALID_ALGORITHMS=("HS256",)):

            resp = self.client.get(self.login_url, follow=True)
            self.assertEqual(200, resp.status_code)
            # Wrong, should redirect to login
            theme_template = "{0}/authorization/login.html".format(
                settings.WIGGUM_DEFAULT_THEME)
            self.assertEqual(theme_template, resp.template_name[0])


    @override_settings(
        JWT_VERSION=2,
        JWT_MINIMUM_VERSION=2.1,
        JWT_COOKIE_CLONE=False,
        FORCE_LOGIN_FORM=False
    )
    def test_jwt_minimum_version_wrong(self):
        body = {
            'username_or_email': self.user.username,
            'password': self.user_password,
            'redirect_uri': "http://google.com",
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check first login
        self.assertEqual(1, len(resp.redirect_chain))
        self.assertEqual(("http://google.com", 302), resp.redirect_chain[0])

        # Check we have cookie
        self.assertIsNotNone(self.client.cookies[settings.JWT_COOKIE_NAME])

        # Check redirect
        resp = self.client.get(self.login_url, follow=True)
        self.assertEqual(200, resp.status_code)

        # Check we have call logout
        self.assertTrue(reverse("auth:logout") in resp.redirect_chain[0][0])
        self.assertTrue(settings.LOGOUT_SUCCESS_REDIRECT in
                        resp.redirect_chain[1][0])

    @override_settings(
        JWT_VERSION=2,
        JWT_MINIMUM_VERSION=2.1,
        JWT_COOKIE_CLONE=False,
        FORCE_LOGIN_FORM=False
    )
    def test_jwt_minimum_version_wrong_redirect(self):
        body = {
            'username_or_email': self.user.username,
            'password': self.user_password,
            'redirect_uri': "http://google.com",
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check first login
        self.assertEqual(1, len(resp.redirect_chain))
        self.assertEqual(("http://google.com", 302), resp.redirect_chain[0])

        # Check we have cookie
        self.assertIsNotNone(self.client.cookies[settings.JWT_COOKIE_NAME])

        # Check redirect
        redirect_logout = body['redirect_uri']
        redirect_param = settings.REDIRECT_URL_VALID_PARAMS[0]
        login_url = "{0}?{1}={2}".format(self.login_url,
                                         redirect_param,
                                         redirect_logout)
        resp = self.client.get(login_url, follow=True)
        self.assertEqual(200, resp.status_code)

        # Check we have call logout
        self.assertTrue(reverse("auth:logout") in resp.redirect_chain[0][0])
        self.assertTrue(redirect_logout in resp.redirect_chain[1][0])

    @override_settings(
        JWT_VERSION=2,
        JWT_MINIMUM_VERSION=1.9,
        JWT_COOKIE_CLONE=False,
        FORCE_LOGIN_FORM=False
    )
    def test_jwt_minimum_version_ok(self):
        body = {
            'username_or_email': self.user.username,
            'password': self.user_password,
            'redirect_uri': "http://google.com",
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check first login
        self.assertEqual(1, len(resp.redirect_chain))
        self.assertEqual(("http://google.com", 302), resp.redirect_chain[0])

        # Check we have cookie
        self.assertIsNotNone(self.client.cookies[settings.JWT_COOKIE_NAME])

        # Check redirect
        resp = self.client.get(self.login_url, follow=True)
        self.assertEqual(200, resp.status_code)

        # Check we have call logout
        self.assertTrue(settings.LOGIN_SUCCESS_REDIRECT in
                        resp.redirect_chain[0][0])

    @override_settings(
        JWT_COOKIE_CLONE=False,
        JWT_COOKIE_DOMAIN="127.0.0.1",
        JWT_COOKIE_DOMAIN_AUTO=True,
        JWT_COOKIE_DOMAIN_AUTO_LEVEL=2)
    def test_login_jwt_cookie_auto_host(self):
        body = {
            'username_or_email': self.user.email,
            'password': self.user_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check
        self.assertEqual(200, resp.status_code)

        # Check cookie ok
        jwt_cookie = self.client.cookies[settings.JWT_COOKIE_NAME]
        self.assertEqual(".0.1", jwt_cookie['domain'])
        self.assertEqual("/", jwt_cookie['path'])
        self.assertEqual(settings.JWT_COOKIE_EXPIRATION_TIME_DELTA,
                         jwt_cookie['max-age'])

        # Check if the jwt is valid (if not valid, decode should
        # throw an exception)
        jwt_encoded = jwt_cookie.value
        jwt_decoded = jwt.decode(jwt_encoded,
                                 settings.JWT_SECRET_KEY,
                                 settings.JWT_SIGN_VALID_ALGORITHMS)

        # Check jwt content ok
        for k, v in jwt_decoded['user'].items():
            self.assertEqual(getattr(self.user, k), v)

        # Check permission
        for k, i in enumerate(self.user.project_permissions.all()):
            self.assertEqual(i.key, jwt_decoded['permission'][k])

    @override_settings(
        JWT_COOKIE_CLONE=False,
        JWT_COOKIE_DOMAIN="127.0.0.1",
        JWT_COOKIE_DOMAIN_AUTO=True,
        JWT_COOKIE_DOMAIN_AUTO_LEVEL=0)
    def test_login_jwt_cookie_auto_host_wrong(self):
        body = {
            'username_or_email': self.user.email,
            'password': self.user_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check
        self.assertEqual(200, resp.status_code)

        # Check cookie ok
        jwt_cookie = self.client.cookies[settings.JWT_COOKIE_NAME]
        self.assertEqual(settings.JWT_COOKIE_DOMAIN, jwt_cookie['domain'])
        self.assertEqual("/", jwt_cookie['path'])
        self.assertEqual(settings.JWT_COOKIE_EXPIRATION_TIME_DELTA,
                         jwt_cookie['max-age'])

        # Check if the jwt is valid (if not valid, decode should
        # throw an exception)
        jwt_encoded = jwt_cookie.value
        jwt_decoded = jwt.decode(jwt_encoded,
                                 settings.JWT_SECRET_KEY,
                                 settings.JWT_SIGN_VALID_ALGORITHMS)

        # Check jwt content ok
        for k, v in jwt_decoded['user'].items():
            self.assertEqual(getattr(self.user, k), v)

        # Check permission
        for k, i in enumerate(self.user.project_permissions.all()):
            self.assertEqual(i.key, jwt_decoded['permission'][k])

    @override_settings(
        JWT_COOKIE_DOMAIN_AUTO=True,
        JWT_COOKIE_DOMAIN_AUTO_LEVEL=2,
        JWT_COOKIE_CLONE=True,
        JWT_COOKIE_CLONE_DOMAINS_ENDPOINT=(
            "login.test1.com", "login.test2.com", "login.test3.com",
            "login.test4.com", "login.test5.com", "login.test6.com",
            "login.test7.com", "login.test8.com", "login.test9.com",
        ),
    )
    def test_login_jwt_cookie_domain_clone(self):
        start_host = settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT[0]

        body = {
            'username_or_email': self.user.email,
            'password': self.user_password,
            'redirect_uri': "http://google.com",
        }

        resp = self.client.post(self.login_url, body, follow=True,
                                SERVER_NAME=start_host, HTTP_HOST=start_host)

        # Check return ok
        self.assertEqual(200, resp.status_code)

        # Check number of redirections
        self.assertEqual(len(resp.redirect_chain),
                         len(settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT[1:])+1)

        # Check clone redirections ok
        for host, redirect in zip(settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT[1:],
                                  resp.redirect_chain[:-1]):

            self.assertTrue(host in redirect[0])
            self.assertEqual(302, redirect[1])

        # Check final redirection
        self.assertEqual(302, resp.redirect_chain[-1][1])
        self.assertEqual(body['redirect_uri'], resp.redirect_chain[-1][0])

        # TODO: Check coockies in all the domains
        # NOTE: Can't check with Django test tools (sets only for the HTTP_HOST domain)

class ResetPasswordTest(TestCase):

    def setUp(self):
        self.login_url = reverse("auth:login")
        self.user = User(username="dark-knight4",
                         email="brucewayne@batman.com",
                         first_name="Bruce",
                         last_name="Wayne")
        self.user.save()
        self.user_password = "dark_knight_password"
        self.new_password = self.user_password + "_new_password"
        self.user.set_password(self.user_password)
        now = timezone.now()
        self.user.password_reset_token_expire = now + datetime.timedelta(
            seconds=5)

        self.user.save()

    def test_password_reset_wrong_user(self):
        url = reverse('auth:reset-password', kwargs={
            'user_id': 999,
            'uuid': str(self.user.password_reset_token)
        })

        body = {
            'password': self.new_password,
            'password2': self.new_password,
        }
        resp = self.client.post(url, body, follow=True)

        theme_template = "{0}/authorization/login.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template,
                         resp.template_name[0])
        self.assertEqual(200, resp.status_code)
        messages = list(resp.context['messages'])
        self.assertEqual(1, len(messages))
        self.assertEqual("Password reset denied", messages[0].message)

    def test_password_reset_wrong_token(self):
        url = reverse('auth:reset-password', kwargs={
            'user_id': self.user.id,
            'uuid': str(uuid.uuid4())
        })

        body = {
            'password': self.new_password,
            'password2': self.new_password,
        }
        resp = self.client.post(url, body, follow=True)
        theme_template = "{0}/authorization/login.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template,
                         resp.template_name[0])
        self.assertEqual(200, resp.status_code)
        messages = list(resp.context['messages'])
        self.assertEqual(1, len(messages))
        self.assertEqual("Password reset denied", messages[0].message)

    def test_password_reset_wrong_expired(self):
        url = reverse('auth:reset-password', kwargs={
            'user_id': self.user.id,
            'uuid': str(self.user.password_reset_token)
        })

        # Set expiration in the past
        now = timezone.now()
        self.user.password_reset_token_expire = now - datetime.timedelta(
            seconds=5)
        self.user.save()

        body = {
            'password': self.new_password,
            'password2': self.new_password,
        }
        resp = self.client.post(url, body, follow=True)
        theme_template = "{0}/authorization/login.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template,
                         resp.template_name[0])
        self.assertEqual(200, resp.status_code)
        messages = list(resp.context['messages'])
        self.assertEqual(1, len(messages))
        self.assertEqual("Token for password reset expired", messages[0].message)

    @override_settings(
        LOGIN_ON_PASSWORD_RESET=False,
        FORCE_LOGIN_FORM=False
    )
    def test_password_reset_not_login(self):
        url = reverse('auth:reset-password', kwargs={
            'user_id': self.user.id,
            'uuid': str(self.user.password_reset_token)
        })

        body = {
            'password': self.new_password,
            'password2': self.new_password,
        }
        resp = self.client.post(url, body, follow=True)
        theme_template = "{0}/authorization/login.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template,
                         resp.template_name[0])
        self.assertEqual(200, resp.status_code)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))
        self.assertIsNone(self.client.cookies.get(settings.JWT_COOKIE_NAME))

    @override_settings(
        LOGIN_ON_PASSWORD_RESET=True,
        FORCE_LOGIN_FORM=False,
        JWT_COOKIE_CLONE=False,
    )
    def test_password_reset_login(self):
        url = reverse('auth:reset-password', kwargs={
            'user_id': self.user.id,
            'uuid': str(self.user.password_reset_token)
        })

        body = {
            'password': self.new_password,
            'password2': self.new_password,
        }
        resp = self.client.post(url, body, follow=True)
        # This will be the login success final redirect (we are already loged)
        theme_template = "{0}/authorization/test_jwt.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template,
                         resp.template_name[0])
        self.assertEqual(200, resp.status_code)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))
        self.assertIsNotNone(self.client.cookies.get(settings.JWT_COOKIE_NAME))


class RecoverPasswordTest(TestCase):

    def setUp(self):
        self.recover_url = reverse("auth:recover-password")
        self.user = User(username="dark-knight4",
                         email="brucewayne@batman.com",
                         first_name="Bruce",
                         last_name="Wayne")
        self.user.save()

    def test_password_recover_inexistent_email(self):
        body = {
            'email': "inexistent@mail.com"
        }
        resp = self.client.post(self.recover_url, body, follow=True)

        theme_template = "{0}/authorization/recover_password.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template,
                         resp.template_name[0])
        self.assertEqual(200, resp.status_code)

        messages = list(resp.context['messages'])
        self.assertEqual(1, len(messages))
        self.assertEqual("We haven't found any account with email inexistent@mail.com",
                         messages[0].message)

    def test_password_recover(self):
        body = {
            'email': self.user.email
        }

        before_token = self.user.password_reset_token
        before_expire = self.user.password_reset_token_expire
        resp = self.client.post(self.recover_url, body, follow=True)

        theme_template = "{0}/authorization/login.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template,
                         resp.template_name[0])
        self.assertEqual(200, resp.status_code)

        self.user.refresh_from_db()
        self.assertNotEqual(before_token, self.user.password_reset_token)
        self.assertTrue(before_expire < self.user.password_reset_token_expire)


@override_settings(
    JWT_COOKIE_DOMAIN_AUTO=True,
    JWT_COOKIE_DOMAIN_AUTO_LEVEL=2,
    JWT_COOKIE_CLONE=True,
    JWT_COOKIE_CLONE_DOMAINS_ENDPOINT=(
        "login.test1.com",
        "login.test2.com",
        "login.test3.com",
    ),
)
class CloneTests(TestCase):

    def setUp(self):
        self.login_url = reverse("auth:login")
        self.user = User(username="dark-knight4",
                         email="brucewayne@batman.com",
                         first_name="Bruce",
                         last_name="Wayne")
        self.user.save()
        self.user_password = "dark_knight_password"
        self.user.set_password(self.user_password)
        self.user.save()

    def test_clone_url(self):
        start_host = settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT[0]
        self.client = Client(SERVER_NAME=start_host, HTTP_HOST=start_host)
        # Create a token
        params = QueryDict(mutable=True)
        params[settings.REDIRECT_URL_VALID_PARAMS[0]] = "http://google.com"
        clone_domains = settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT
        params.setlist('clone-domains', clone_domains)
        jwt_token = jwt_utils.create_jwt(self.user)
        url_path = reverse('auth:clone-cookie', kwargs={'token': jwt_token})

        url = urllib.parse.ParseResult(
            scheme="",
            netloc="",
            path=url_path,
            params="",
            query=params.urlencode(),
            fragment="",
        )
        resp = self.client.get(url.geturl(), follow=True)
        self.assertEqual(200, resp.status_code)

        # Check cloning redirects
        for k, i in enumerate(resp.redirect_chain[:-1]):
            clone_domains = list(settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT)
            params = QueryDict(mutable=True)
            params[settings.REDIRECT_URL_VALID_PARAMS[0]] = "http://google.com"
            params.setlist('clone-domains', clone_domains[k+1:])

            clone_domains = clone_domains[k:]
            if len(clone_domains) > 0:
                next_host = clone_domains[0]
            else:
                next_host = ""

            url = urllib.parse.ParseResult(
                scheme="http",
                netloc=next_host,
                path=url_path,
                params="",
                query=params.urlencode(),
                fragment="",
            )

        # Final redirect (redirect uri)
        self.assertEqual(302, resp.redirect_chain[-1][1])
        self.assertEqual(params[settings.REDIRECT_URL_VALID_PARAMS[0]],
                         resp.redirect_chain[-1][0])


@override_settings(
    FORCE_LOGIN_FORM=False,
    JWT_COOKIE_DOMAIN_AUTO=True,
)
class LogoutTests(TestCase):

    def setUp(self):
        self.login_url = reverse("auth:login")
        self.user = User(username="dark-knight4",
                         email="brucewayne@batman.com",
                         first_name="Bruce",
                         last_name="Wayne")
        self.user.save()
        self.user_password = "dark_knight_password"
        self.user.set_password(self.user_password)
        self.user.save()

        self.login_url = reverse("auth:login")
        self.logout_url = reverse("auth:logout")

    @override_settings(
        JWT_COOKIE_CLONE=False,
        ALLOWED_HOSTS=("login.test1.com",)
    )
    def test_logout_single_domain(self):
        # Set the correct client
        start_host = settings.ALLOWED_HOSTS[0]
        self.client = Client(SERVER_NAME=start_host, HTTP_HOST=start_host)

        redirect_url = "https://google.com"
        redirect_param = settings.REDIRECT_URL_VALID_PARAMS[0]
        url = "{0}?{1}={2}".format(self.login_url, redirect_param, redirect_url)

        # check not logged
        resp = self.client.get(url, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual([], resp.redirect_chain)

        # Login
        body = {
            'username_or_email': self.user.email,
            'password': self.user_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)
        self.assertEqual(200, resp.status_code)

        # Check logged
        resp = self.client.get(url, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual([(redirect_url, 302), ], resp.redirect_chain)
        self.assertIsNotNone(self.client.cookies.get(settings.JWT_COOKIE_NAME))

        # Logout
        resp = self.client.get(self.logout_url, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.redirect_chain))

        # Check logout
        resp = self.client.get(url, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual([], resp.redirect_chain)

    @override_settings(
        JWT_COOKIE_CLONE=False,
        ALLOWED_HOSTS=("login.test1.com",)
    )
    def test_logout_single_domain_redirect(self):
        # Set the correct client
        start_host = settings.ALLOWED_HOSTS[0]
        self.client = Client(SERVER_NAME=start_host, HTTP_HOST=start_host)

        redirect_url = "https://google.com"
        redirect_param = settings.REDIRECT_URL_VALID_PARAMS[0]
        url = "{0}?{1}={2}".format(self.login_url, redirect_param, redirect_url)
        url_logout = "{0}?{1}={2}".format(self.logout_url,
                                          redirect_param,
                                          redirect_url)

        # check not logged
        resp = self.client.get(url, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual([], resp.redirect_chain)

        # Login
        body = {
            'username_or_email': self.user.email,
            'password': self.user_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)
        self.assertEqual(200, resp.status_code)

        # Check logged
        resp = self.client.get(url, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual([(redirect_url, 302), ], resp.redirect_chain)
        self.assertIsNotNone(self.client.cookies.get(settings.JWT_COOKIE_NAME))

        # Logout
        resp = self.client.get(url_logout, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.redirect_chain))
        self.assertEqual([(redirect_url, 302), ], resp.redirect_chain)

        # Check logout
        resp = self.client.get(url, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual([], resp.redirect_chain)

    @override_settings(
        JWT_COOKIE_CLONE=True,
        JWT_COOKIE_CLONE_DOMAINS_ENDPOINT=(
            "login.test1.com",
            "login.test2.com",
            "login.test3.com",
        ),
    )
    def test_logout_multiple_domains(self):
        # Set the correct client
        start_host = settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT[0]
        self.client = Client(SERVER_NAME=start_host, HTTP_HOST=start_host)

        redirect_url = "https://google.com"
        redirect_param = settings.REDIRECT_URL_VALID_PARAMS[0]
        url = "{0}?{1}={2}".format(self.login_url, redirect_param, redirect_url)

        # check not logged
        resp = self.client.get(url, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual([], resp.redirect_chain)

        # Login
        body = {
            'username_or_email': self.user.email,
            'password': self.user_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(len(settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT[1:])+1,
                         len(resp.redirect_chain))

        # Check logged
        resp = self.client.get(url, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(redirect_url, resp.redirect_chain[0][0])
        self.assertIsNotNone(self.client.cookies.get(settings.JWT_COOKIE_NAME))

        # Logout
        resp = self.client.get(self.logout_url, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(len(settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT[1:])+1,
                         len(resp.redirect_chain))

        # Check logout
        resp = self.client.get(url, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual([], resp.redirect_chain)

    @override_settings(
        JWT_COOKIE_CLONE=True,
        JWT_COOKIE_CLONE_DOMAINS_ENDPOINT=(
            "login.test1.com",
            "login.test2.com",
            "login.test3.com",
        ),
    )
    def test_logout_multiple_domains_redirect(self):
        # Set the correct client
        start_host = settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT[0]
        self.client = Client(SERVER_NAME=start_host, HTTP_HOST=start_host)

        redirect_url = "https://google.com"
        redirect_param = settings.REDIRECT_URL_VALID_PARAMS[0]
        url = "{0}?{1}={2}".format(self.login_url, redirect_param, redirect_url)
        url_logout = "{0}?{1}={2}".format(self.logout_url,
                                          redirect_param,
                                          redirect_url)

        # check not logged
        resp = self.client.get(url, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual([], resp.redirect_chain)

        # Login
        body = {
            'username_or_email': self.user.email,
            'password': self.user_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)
        self.assertEqual(len(settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT[1:])+1,
                         len(resp.redirect_chain))
        self.assertEqual(200, resp.status_code)

        # Check logged
        resp = self.client.get(url, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(redirect_url, resp.redirect_chain[0][0])
        self.assertIsNotNone(self.client.cookies.get(settings.JWT_COOKIE_NAME))

        # Logout
        resp = self.client.get(url_logout, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(len(settings.JWT_COOKIE_CLONE_DOMAINS_ENDPOINT[1:])+1,
                         len(resp.redirect_chain))
        self.assertEqual((redirect_url, 302), resp.redirect_chain[-1])

        # Check logout
        resp = self.client.get(url, follow=True)
        self.assertEqual(200, resp.status_code)
        self.assertEqual([], resp.redirect_chain)

@override_settings(
    FORCE_LOGIN_FORM=False,
    JWT_COOKIE_DOMAIN_AUTO=True,
    JWT_IMPERSONATE_ENABLE=True,
)
class ImpersonateTests(TestCase):
    def setUp(self):

        # User 1 (can impersonate user 2)
        self.user = User(username="dark-knight4",
                         email="brucewayne@batman.com",
                         first_name="Bruce",
                         last_name="Wayne")
        self.user.save()
        self.user_password = "dark_knight_password"
        self.user.set_password(self.user_password)
        self.user.save()
        p = ProjectPermission.objects.get(key=settings.APP_PERMISSION_KEYS['impersonate'])
        self.user.project_permissions.add(p)
        self.user.save()

        # User 2 (can't impersonate user 1)
        self.user2 = User(username="spiderman1",
                                      email="peterparker@spiderman.com",
                                      first_name="Peter",
                                      last_name="Parker")
        self.user2.save()
        self.user2_password = "spiderman_password"
        self.user2.set_password(self.user2_password)
        self.user2.save()

        # Urls
        self.login_url = reverse("auth:login")
        self.impersonate_user1_url = reverse("auth:impersonate",
                                             args=[self.user.id])
        self.impersonate_user2_url = reverse("auth:impersonate",
                                             args=[self.user2.id])

    @override_settings(
        JWT_IMPERSONATE_ENABLE=False,
    )
    def test_impersonate_disabled(self):
        # login with user 1
        body = {
            'username_or_email': self.user.email,
            'password': self.user_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check
        theme_template = "{0}/authorization/test_jwt.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])
        self.assertEqual(200, resp.status_code)

        # Impersonate user 2
        resp = self.client.get(self.impersonate_user2_url, follow=True)
        self.assertEqual(200, resp.status_code)
        theme_template = "{0}/authorization/test_jwt.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])

        # Check message
        messages = list(resp.context['messages'])
        self.assertEqual(1, len(messages))
        self.assertEqual("Impersonation not active", messages[0].message)

    def test_impersonate_no_permission(self):
        # login with user 2
        body = {
            'username_or_email': self.user2.email,
            'password': self.user2_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check
        theme_template = "{0}/authorization/test_jwt.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])
        self.assertEqual(200, resp.status_code)

        # Impersonate user 1
        resp = self.client.get(self.impersonate_user1_url, follow=True)
        self.assertEqual(200, resp.status_code)
        theme_template = "{0}/authorization/test_jwt.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])

        # Check message
        messages = list(resp.context['messages'])
        self.assertEqual(1, len(messages))
        self.assertEqual("You don't have impersonation permission", messages[0].message)

    def test_impersonate_itself(self):
        # login with user 1
        body = {
            'username_or_email': self.user.email,
            'password': self.user_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check
        theme_template = "{0}/authorization/test_jwt.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])
        self.assertEqual(200, resp.status_code)

        # Impersonate user 1
        resp = self.client.get(self.impersonate_user1_url, follow=True)
        self.assertEqual(200, resp.status_code)
        theme_template = "{0}/authorization/test_jwt.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])

        # Check message
        messages = list(resp.context['messages'])
        self.assertEqual(1, len(messages))
        self.assertEqual("Can't impersonate yourself", messages[0].message)

    def test_impersonate_ok(self):
        # login with user 1
        body = {
            'username_or_email': self.user.email,
            'password': self.user_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check
        theme_template = "{0}/authorization/test_jwt.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])
        self.assertEqual(200, resp.status_code)

        # Impersonate user 2
        resp = self.client.get(self.impersonate_user2_url, follow=True)
        self.assertEqual(200, resp.status_code)
        theme_template = "{0}/authorization/test_jwt.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])

        # Check jwt token
        jwt_cookie = self.client.cookies[settings.JWT_COOKIE_NAME]
        jwt_encoded = jwt_cookie.value
        jwt_decoded = jwt.decode(jwt_encoded,
                                 settings.JWT_SECRET_KEY,
                                 settings.JWT_SIGN_VALID_ALGORITHMS)

        # Check jwt content ok
        for k, v in jwt_decoded['user'].items():
            self.assertEqual(getattr(self.user2, k), v)

        # Check impersonate flags
        self.assertTrue(jwt_decoded['impersonate'])
        self.assertEquals(self.user.id, jwt_decoded['real_user_id'])

    def test_impersonate_wrong_user(self):
        # login with user 1
        body = {
            'username_or_email': self.user.email,
            'password': self.user_password,
        }
        resp = self.client.post(self.login_url, body, follow=True)

        # Check
        theme_template = "{0}/authorization/test_jwt.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])
        self.assertEqual(200, resp.status_code)

        # Impersonate user 12345
        resp = self.client.get(
            reverse("auth:impersonate", args=[12345]), follow=True)
        self.assertEqual(200, resp.status_code)
        theme_template = "{0}/authorization/test_jwt.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])

        # Check message
        messages = list(resp.context['messages'])
        self.assertEqual(1, len(messages))
        self.assertEqual("Invalid user for impersonation", messages[0].message)

    def test_impersonate_no_logged(self):
        # Impersonate user 2
        resp = self.client.get(self.impersonate_user2_url, follow=True)
        self.assertEqual(200, resp.status_code)
        redirect_param = settings.REDIRECT_URL_VALID_PARAMS[0]
        url = 'http://testserver/a/login/?{0}=/a/impersonate/{1}'.format(
            redirect_param,
            self.user2.id
        )
        self.assertEqual([(url, 302), ], resp.redirect_chain)

@override_settings(
    FORCE_LOGIN_FORM=False,
    JWT_COOKIE_DOMAIN_AUTO=True,
    JWT_SFA_ENABLE=True,
)
class SFATests(TestCase):
    def setUp(self):
        self.user = User(username="dark-knight4",
                         email="brucewayne@batman.com",
                         first_name="Bruce",
                         last_name="Wayne")
        self.user_password = "dark_knight_password"
        self.user.set_password(self.user_password)
        self.user.save()
        self.login_url = reverse("auth:login")

    @override_settings(
        JWT_SFA_ENABLE=False,
    )
    def test_sfa_disabled(self):
        # Check not logged
        resp = self.client.get(self.login_url, follow=True)
        self.assertEqual(200, resp.status_code)
        theme_template = "{0}/authorization/login.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])
        self.assertEqual(0, len(resp.redirect_chain))

        # Create an sfa link
        refresh_sfa_token(self.user)
        sfa_url = reverse('auth:sfa', kwargs={
            'user_id': self.user.id,
            'uuid': str(self.user.sfa_token)
        })

        # Check message
        resp = self.client.get(sfa_url, follow=True)
        messages = list(resp.context['messages'])
        self.assertEqual(1, len(messages))
        self.assertEqual("SFA not active", messages[0].message)

    def test_sfa_wrong_token(self):
        # Check not logged
        resp = self.client.get(self.login_url, follow=True)
        self.assertEqual(200, resp.status_code)
        theme_template = "{0}/authorization/login.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])
        self.assertEqual(0, len(resp.redirect_chain))

        # Create an sfa link
        refresh_sfa_token(self.user)
        sfa_url = reverse('auth:sfa', kwargs={
            'user_id': self.user.id,
            'uuid':  str(uuid.uuid4())
        })

        # Check message
        resp = self.client.get(sfa_url, follow=True)
        messages = list(resp.context['messages'])
        self.assertEqual(1, len(messages))
        self.assertEqual("Invalid SFA token", messages[0].message)

    def test_sfa_expired(self):
        # Check not logged
        resp = self.client.get(self.login_url, follow=True)
        self.assertEqual(200, resp.status_code)
        theme_template = "{0}/authorization/login.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])
        self.assertEqual(0, len(resp.redirect_chain))

        # Create an sfa link
        refresh_sfa_token(self.user, seconds=1)
        sfa_url = reverse('auth:sfa', kwargs={
            'user_id': self.user.id,
            'uuid': str(self.user.sfa_token)
        })
        time.sleep(1.2 * settings.SECOND)

        # Check message
        resp = self.client.get(sfa_url, follow=True)
        messages = list(resp.context['messages'])
        self.assertEqual(1, len(messages))
        self.assertEqual("SFA link expired", messages[0].message)

    def test_sfa_ok(self):
        # Check not logged
        resp = self.client.get(self.login_url, follow=True)
        self.assertEqual(200, resp.status_code)
        theme_template = "{0}/authorization/login.html".format(
            settings.WIGGUM_DEFAULT_THEME)
        self.assertEqual(theme_template, resp.template_name[0])
        self.assertEqual(0, len(resp.redirect_chain))

        # Create an sfa link
        refresh_sfa_token(self.user)
        sfa_url = reverse('auth:sfa', kwargs={
            'user_id': self.user.id,
            'uuid': str(self.user.sfa_token)
        })

        resp = self.client.get(sfa_url, follow=True)
        self.assertEqual(200, resp.status_code)
        messages = list(resp.context['messages'])
        self.assertEqual(0, len(messages))

        # Check logged
        jwt_cookie = self.client.cookies[settings.JWT_COOKIE_NAME]
        jwt_encoded = jwt_cookie.value
        jwt_decoded = jwt.decode(jwt_encoded,
                                 settings.JWT_SECRET_KEY,
                                 settings.JWT_SIGN_VALID_ALGORITHMS)

        # Check jwt content ok
        for k, v in jwt_decoded['user'].items():
            self.assertEqual(getattr(self.user, k), v)
