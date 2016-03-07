import datetime

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
import jwt

from users.models import User
from . import jwt_utils

priv_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAxwUlmffoMOQQyhRKfcOP76xg1YEt9IhrA5mBm0WvgxHNRL7T
OdciWZJUnpwv4X9S5uPEWnQcQYX1GvHR8ROv0cjT1mAzXGPDWmInf6oKbLAetgJj
muUrIP4B+mdhVB7rvwLQK0T2HJPlkLVaflM/RHsrD1tET7oGge1IyXOfRQBZ1Qxf
F3GNyN/uQfX9uRMKV4A51nKNGOnaIJXeIeMfyRxY0sNZD1SWzgjeVA+rAN1v2Yq1
Pi2I3xXHiYwD/nR67/mCvthX0LnSylaO7LxGRcc/vPljP9GL18+jm1BOchwjjV8p
on7RksVX1dx+pWilRojXN4kpe7ek8/8V2nt1LwIDAQABAoIBAAnICfoQQhwtCVo1
NxgJRYi9CyFTMQQEtGW/5KvR9/dUJ6eKTW1ZUnnehEQrXvsRO+zXIu5jKIRb5hkF
65CSrCB+Y1L09XFEAfTuQAy5ObvvyAKgCW8ydjUv5r78176/qkyAAeUuhX4QEsdS
8nik9MYT26DslmXouasnE127TgehD37B3GwCO2ypYtiFmGsu3dycL/IzboPviyFH
zIp8gu8h/NtqTGEK5kivw6dASg0iBk77SYQGvfNDxZNHt/DeagMvPe77NjrrTyV2
+nnSi1yvpiw9nGRF3TGbFgtTfJfPf2ptaqX+k7/1KQ+Mu3z2LYhRJCvCuDEUZIe2
ehGDXGECgYEA+JNP4IRoDq+XjuY0/IniCaogz1MFswzQfPT865ljRS3Q3TrDBXJ6
DlH0wAgPs7Lb5wlGN1OPEp9JEi8Y6rBxVGiqTMwkcpNa/jN5uJafIYnKbCIwn4Dz
gHp6pWrATyXSWtp4DSho/JrTK4bJpT2jyCud8BWz0DfMS309yHEsJJECgYEAzPbr
NqggWhH8Wc1ffUSMZjZ4FvNhWZS3wlw+b4ezUpFdw31dGCLArTySTZXXArdPEf4o
oof3Pb1Rczkf8mSirFKYUk3aWKHJzZz4+jJtKeHRhaUiNQL1xXc4P+K1/o8fUxOk
LzN9klK3rO2R7qaBB4HeOh2M3j+pGHEw6FDL3b8CgYBHOR5X/Fg8bP+GCFwCSBem
IUMJZIZriS5rv16AuxCAj+IaoW2jr+tdEwqHw0eMe6Eaj8O4so56DX3IYgpHpIq0
XtD89Dk1Qxd9Yo5r32x1FaAUX6+C5FXg6DcgEnhLtVCSi6p+SqfaSRpcjGBWolS9
VBIK6oz9Ch/VOWtsdVDqoQKBgB4dRU/hgedZ7ybOmvIPyUUXSautlKcRx7IB1ZaT
bJB8FTesyqnKKV8KoEBP/KhEgJSXMCc5LOVgVIBGa2A00wXYmNK255bQJpNUNeyk
zg8yQ5OMQKtjRPL/Yj9Ysv60zphpMV1SBmgiSSRaP2+9/QU6WolVYCYjWlfiAZqQ
jHOHAoGAGsHfQXmB2duOUOX+Y9ERN5L+5EQPKDHRZ5CeE2RpH7hvdfyXVntdCyGU
Hs1Mi73djZAlVwB0iepRjarj6gHSNQQranKH8BvITOfyuNnJ8eceWHXxoeVjMWpJ
a1RTohl9dIV5bK9xQD23rfaaebnddCbf8vpKoIW4HoQD0dnEprA=
-----END RSA PRIVATE KEY-----"""
pub_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDHBSWZ9+gw5BDKFEp9w4/vrGDVgS30iGsDmYGbRa+DEc1EvtM51yJZklSenC/hf1Lm48RadBxBhfUa8dHxE6/RyNPWYDNcY8NaYid/qgpssB62AmOa5Ssg/gH6Z2FUHuu/AtArRPYck+WQtVp+Uz9EeysPW0RPugaB7UjJc59FAFnVDF8XcY3I3+5B9f25EwpXgDnWco0Y6dogld4h4x/JHFjSw1kPVJbOCN5UD6sA3W/ZirU+LYjfFceJjAP+dHrv+YK+2FfQudLKVo7svEZFxz+8+WM/0YvXz6ObUE5yHCONXymiftGSxVfV3H6laKVGiNc3iSl7t6Tz/xXae3Uv slok@gondor"
asymm_alg = "RS256"
symm_priv_key = "test1"
symm_priv_key2 = "test2"
symm_alg = "HS256"


@override_settings(
    JWT_SECRET_KEY=symm_priv_key,
    JWT_VERIFICATION_KEY=symm_priv_key,
    JWT_TRANSITION_VERIFICATION_KEY=symm_priv_key2,
    JWT_SIGN_ALGORITHM=symm_alg,
    JWT_TRANSITION_ENABLE=True,
    JWT_SIGN_VALID_ALGORITHMS=(symm_alg,)
)
class JwtUtilsTest(TestCase):

    def setUp(self):
        self.user = User(username="dark-knight4",
                         email="brucewayne@batman.com",
                         first_name="Bruce",
                         last_name="Wayne")
        self.user.save()

    def test_create_jwt_payload(self):
        expiration_delta = 10 * settings.SECOND
        now = timezone.now()
        expiration_date = int((now + datetime.timedelta(
                              seconds=expiration_delta)).strftime("%s"))
        now_date = int((now).strftime("%s"))
        now_nbf = int((now - datetime.timedelta(
            seconds=settings.JWT_NBF_LEEWAY_SECONDS)).strftime("%s"))

        issuer = "wiggum_test"
        extra_args = {
            'extra1': "extra 1",
            'extra2': "extra 2",
        }
        payload = jwt_utils.create_jwt_payload(self.user, expiration_delta,
                                               issuer, **extra_args)

        # Check user
        for k, v in payload['user'].items():
            self.assertEqual(getattr(self.user, k), v)

        # Check permission
        for k, i in enumerate(self.user.project_permissions.all()):
            self.assertEqual(i.key, payload['permission'][k])

        # Check claims
        self.assertEqual(expiration_date, payload['exp'])
        self.assertEqual(issuer, payload['iss'])
        self.assertEqual(now_nbf, payload['nbf'])
        self.assertEqual(now_date, payload['iat'])

        # Check extra args
        self.assertEqual(extra_args['extra1'], payload['extra1'])
        self.assertEqual(extra_args['extra2'], payload['extra2'])


    def test_valid_create_jwt(self):
        encoded_jwt = jwt_utils.create_jwt(self.user)

        # Check bad signed
        with self.assertRaises(jwt.exceptions.DecodeError) as de:
            jwt.decode(encoded_jwt, "wrong_key")
        self.assertEqual(str(de.exception), "Signature verification failed")

        # Check good signed
        jwt_decoded = jwt.decode(encoded_jwt, settings.JWT_SECRET_KEY)

        # Simple payload check
        for k, v in jwt_decoded['user'].items():
            self.assertEqual(getattr(self.user, k), v)

    def test_valid_jwt(self):
        encoded_jwt = jwt_utils.create_jwt(self.user)

        self.assertTrue(jwt_utils.valid_jwt(encoded_jwt,
                                            settings.JWT_SECRET_KEY,
                                            settings.JWT_SIGN_VALID_ALGORITHMS))
        self.assertFalse(jwt_utils.valid_jwt(encoded_jwt,
                                             "wrong_key",
                                             settings.JWT_SIGN_VALID_ALGORITHMS))
        self.assertFalse(jwt_utils.valid_jwt(encoded_jwt,
                                             settings.JWT_SECRET_KEY,
                                             None))

    def test_validate_jwt_all_keys_main_ok(self):
        encoded_jwt = jwt_utils.create_jwt(self.user)

        self.assertTrue(jwt_utils.validate_jwt_all_keys(encoded_jwt))

    def test_validate_jwt_all_keys_transition_ok(self):
        encoded_jwt = jwt_utils.create_jwt(
            self.user,
            symm_priv_key2,
            settings.JWT_SIGN_ALGORITHM)

        # Check the main key is not valid
        self.assertFalse(jwt_utils.valid_jwt(encoded_jwt,
                                             settings.JWT_SECRET_KEY,
                                             settings.JWT_SIGN_VALID_ALGORITHMS))

        self.assertTrue(jwt_utils.validate_jwt_all_keys(encoded_jwt))

    def validate_jwt_all_keys_wrong(self):
        encoded_jwt = jwt_utils.create_jwt(self.user, "wrong")

        self.assertFalse(jwt_utils.validate_jwt_all_keys(encoded_jwt))

    def test_decode_jwt(self):
        encoded_jwt = jwt_utils.create_jwt(self.user)
        decoded_jwt = jwt_utils.decode_jwt(encoded_jwt)

        # Basic check (no claims)
        for k, v in decoded_jwt['user'].items():
            self.assertEqual(getattr(self.user, k), v)
        for k, i in enumerate(self.user.project_permissions.all()):
            self.assertEqual(i.key, decoded_jwt['permission'][k])

    @override_settings(
        JWT_SECRET_KEY=priv_key,
        JWT_VERIFICATION_KEY=pub_key,
        JWT_SIGN_ALGORITHM=asymm_alg,
        JWT_SIGN_VALID_ALGORITHMS=(asymm_alg,)
    )
    def test_asymmetric_jwt(self):
        encoded_jwt = jwt_utils.create_jwt(self.user)

        self.assertFalse(jwt_utils.valid_jwt(encoded_jwt,
                                             settings.JWT_SECRET_KEY,
                                             settings.JWT_SIGN_VALID_ALGORITHMS))

        self.assertTrue(jwt_utils.valid_jwt(encoded_jwt,
                                            settings.JWT_VERIFICATION_KEY,
                                            settings.JWT_SIGN_VALID_ALGORITHMS))

    @override_settings(
        JWT_SECRET_KEY=priv_key,
        JWT_VERIFICATION_KEY=pub_key,
        JWT_SIGN_ALGORITHM=asymm_alg,
        JWT_SIGN_VALID_ALGORITHMS=(asymm_alg,)
    )
    def test_asymmetric_jwt_guess(self):
        encoded_jwt = jwt_utils.create_jwt(self.user)
        self.assertTrue(jwt_utils.validate_jwt_all_keys(encoded_jwt))

    @override_settings(
        JWT_TRANSITION_VERIFICATION_KEY=pub_key,
        JWT_SIGN_VALID_ALGORITHMS=(asymm_alg),
        JWT_TRANSITION_ENABLE=True
    )
    def test_asymmetric_jwt_guess_transition(self):
        encoded_jwt = jwt_utils.create_jwt(self.user, priv_key, asymm_alg)

        self.assertFalse(jwt_utils.valid_jwt(encoded_jwt,
                                             settings.JWT_VERIFICATION_KEY,
                                             settings.JWT_SIGN_VALID_ALGORITHMS))

        self.assertTrue(jwt_utils.validate_jwt_all_keys(encoded_jwt))

    @override_settings(
        JWT_VERIFICATION_KEY=pub_key,
        JWT_TRANSITION_VERIFICATION_KEY=symm_priv_key,
        JWT_SIGN_VALID_ALGORITHMS=(asymm_alg, symm_alg),
        JWT_TRANSITION_ENABLE=True
    )
    def test_key_symm_asymm_mix(self):
        encoded_jwt = jwt_utils.create_jwt(self.user, symm_priv_key, symm_alg)

        self.assertTrue(jwt_utils.validate_jwt_all_keys(encoded_jwt))
