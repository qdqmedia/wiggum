from .base import *


# Wiggum editable settings

# ----------------------------------------- #
#            App permission stuff           #
# ----------------------------------------- #

# App permissions for the wiggum applications
APP_PERMISSION_KEYS = {
    'admin': "wiggum.all",                           # Admin
    'impersonate': "wiggum.impersonate",             # Impersonate user sessions
}

# ----------------------------------------- #
#               API stuff                   #
# ----------------------------------------- #

# Wiggum api version
API_VERSION = "v1"

# ----------------------------------------- #
#               JWT stuff                   #
# ----------------------------------------- #

# Json web token secret key (private key if is an asymmetric sign)
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', None)

# Verification key
#   - if symmetric, this should be the same as the JWT_SECRET_KEY)
#   - If asymmetric, this sould be the public key
JWT_VERIFICATION_KEY = os.getenv('JWT_VERIFICATION_KEY', None)

# Json web token algorithm to sign
JWT_SIGN_ALGORITHM = os.getenv('JWT_SIGN_ALGORITHM', "HS256")

# JWT retrocompatibility Settings
# If this settings is true then a second key will be used to validate a user
# Normally this would be the old key
JWT_TRANSITION_ENABLE = True if os.getenv('JWT_TRANSITION_ENABLE', False) in ("True", "true", "Yes", "yes", "y") else False

# This key will be checked as a second valid key (used for transitions between
# one key and a new one without affecting the users)
JWT_TRANSITION_VERIFICATION_KEY = os.getenv('JWT_TRANSITION_VERIFICATION_KEY', None)

# List of supported sign algorithms by Wiggum for decoding
JWT_SIGN_VALID_ALGORITHMS = os.getenv('JWT_SIGN_VALID_ALGORITHMS', "HS256 RS256").split()


# The max time to invalidate the token (in seconds)
JWT_EXPIRATION_TIME_DELTA = 15 * DAY

# Small amount of time in seconds to allow time difference between systems
JWT_NBF_LEEWAY_SECONDS = 15

# The issuer of the json web token
JWT_ISSUER = os.getenv('JWT_ISSUER', "wiggumio")

# The jwt key on the cookie
JWT_COOKIE_NAME = "wiggumio_jwt"

# The domain/subdomain/domain-wilcard  where the cookie will be sent
JWT_COOKIE_DOMAIN = ".wiggum.io"  # We use JWT_COOKIE_DOMAIN_AUTO


# The jwt token cookie expiration
JWT_COOKIE_EXPIRATION_TIME_DELTA = JWT_EXPIRATION_TIME_DELTA

# Only use jwt on https cookies
JWT_COOKIE_ONLY_HTTPS = False

# If you want to set the cookie to the domain of the request automatically
JWT_COOKIE_DOMAIN_AUTO = True

# Auto domain level for the automatic cookie domain based on the request.
# If you set the level to be less or equal than 1, then will set the
# request domain as it is.
# User request from: login.production.wiggum.org
# level 2: .wiggum.org
# level 3: .production.wiggum.org
# User request from: login.staging.wiggum2.com
# level 4: .login.staging.wiggum2.com
JWT_COOKIE_DOMAIN_AUTO_LEVEL = 2

# Activate the cookie cloning for multiple domains
JWT_COOKIE_CLONE = True if os.getenv('JWT_COOKIE_CLONE', True) in ("True", "true", "Yes", "yes", "y") else False

# The wiggum subdomains to clone  the cookie
JWT_COOKIE_CLONE_DOMAINS_ENDPOINT = (
    "login.wiggum.io",
    "login2.wiggum.io",
)

# Appart from the user basic information set the permissions of the user on the
# jwt token
JWT_SET_PERMISSION_ON_TOKEN = False

# The version of the jwt token
JWT_VERSION = 1.1

# The minimum version of token that is valid
JWT_MINIMUM_VERSION = 1

# Logout the user if the version of the token is lesser than the minimum version
JWT_DESTROY_TOKEN_ON_LESSER_VERSION = True

# If impersonate is enable then an admin with the 'wiggum.all' or
# 'wiggum.impersonate' permission could create a jwt token of any user
# Note: Will destroy de current key (session logout)
# Note2: With a great power comes great responsibility
JWT_IMPERSONATE_ENABLE = True

# The time the jwt token will be valid for an impersonated token
JWT_IMPERSONATE_EXPIRATION_TIME_DELTA = 1 * HOUR

# The time the cookie will be valid for an impersonated token cookie
JWT_IMPERSONATE_COOKIE_EXPIRATION_TIME_DELTA = JWT_IMPERSONATE_EXPIRATION_TIME_DELTA

# Activate SFA (Single factor authentication) based on a url
JWT_SFA_ENABLE = True

# SFA token expiration seconds
JWT_SFA_EXPIRE_DELTA = 1 * HOUR

#
# ----------------------------------------- #
#                 ACTIONS                   #
# ----------------------------------------- #

LOGIN_PRE_CHECK = (
    "authorization.actions.login_pre_check.ForceLoginFormAction",
    "authorization.actions.login_pre_check.CheckUserAuthenticatedAlreadyAction",
    "authorization.actions.login_pre_check.CheckValidJWTVersionAction",
)

LOGIN_SUCCESS_ACTIONS = (
    "authorization.actions.login_success.CreateJWTAction",
    "authorization.actions.login_success.RedirectToCloneJWTSessionAction",
    "authorization.actions.login_success.SetJWTOnCookieAction",
    "authorization.actions.login_success.LoginSuccessMetricAction",
)

LOGIN_FAILURE_ACTIONS = (
    "authorization.actions.login_failure.AuthenticationErrorMessageAction",
    "authorization.actions.login_failure.LoginFailureMetricAction",
)

LOGOUT_ACTIONS = (
    "authorization.actions.logout.DeleteDjangoAuthSessionAction",
    "authorization.actions.logout.JWTDeleteCookieAction",
    "authorization.actions.logout.LogoutMetricsAction",
)

CLONE_ACTIONS = (
    "authorization.actions.login_success.SetJWTOnCookieAction",
)

RECOVER_PASS_REQUEST_ACTIONS = (
    "authorization.actions.recover_pass_request.LoadUserFromDatabaseAction",
    "authorization.actions.recover_pass_request.CheckUserCorrectAction",
    "authorization.actions.recover_pass_request.CreateRecoverPasswordTokenAction",
    "authorization.actions.recover_pass_request.PasswordResetRequestMetricAction",
)

RESET_PASS_ACTIONS = (
    "authorization.actions.reset_pass.CreateJwtOnViewOnPassResetAction",
    "authorization.actions.reset_pass.RedirectToCloneJWTSessionOnPassResetAction",
    "authorization.actions.reset_pass.SetJWTOnCookieOnPassResetAction",
    "authorization.actions.reset_pass.PasswordResetMetricAction",

)

IMPERSONATE_ACTIONS = (
    "authorization.actions.impersonate.CheckImpersonateActiveAction",
    "authorization.actions.impersonate.RedirectToLoginIfNotAuthenticatedAction",
    "authorization.actions.login_pre_check.CheckValidJWTVersionAction",
    "authorization.actions.impersonate.CheckImpersonatePermissionAction",
    "authorization.actions.impersonate.CheckImpersonateSameUserAction",
    "authorization.actions.impersonate.CreateImpersonateJWTAction",
    "authorization.actions.login_success.RedirectToCloneJWTSessionAction",
    "authorization.actions.impersonate.SetImpersonateJWTOnCookieAction",
    "authorization.actions.impersonate.ImpersonationMetricAction",
)

SFA_ACTIONS = (
    "authorization.actions.sfa.CheckSFAActiveAction",
    "authorization.actions.login_success.CreateJWTAction",
    "authorization.actions.login_success.RedirectToCloneJWTSessionAction",
    "authorization.actions.login_success.SetJWTOnCookieAction",
    "authorization.actions.sfa.ResetSFATokenAction",
)

# ----------------------------------------- #
#           DEFAULT REDIRECTIONS            #
# ----------------------------------------- #

LOGIN_SUCCESS_REDIRECT = "/a/test/jwt"  # reverse_lazy('auth:test-jwt')
LOGOUT_SUCCESS_REDIRECT = "/a/test/jwt"  # reverse_lazy('auth:test-jwt')
CLONE_SUCCESS_REDIRECT = "/a/test/jwt"  # reverse_lazy('auth:test-jwt')
RECOVER_PASS_REQUEST_SUCCESS_REDIRECT = "/a/login"  # reverse_lazy('auth:login')
RESET_PASS_SUCCESS_REDIRECT = "/a/login"  # reverse_lazy('auth:login')
IMPERSONATE_SUCCESS_REDIRECT = "/a/test/jwt" # reverse_lazy('auth:test-jwt')
SFA_SUCCESS_REDIRECT = "/a/login"  # reverse_lazy('auth:login')

# ----------------------------------------- #
#             PASSWORD RESET                #
# ----------------------------------------- #

PASSWORD_RESET_EXPIRE_DELTA = 12 * HOUR

# Log in the user on password reset
LOGIN_ON_PASSWORD_RESET = True

# ----------------------------------------- #
#             AUTH BACKENDS                 #
# ----------------------------------------- #

# Set the backends for authentication in order
WIGGUM_AUTHENTICATION_BACKENDS = (
    "authorization.backends.JWTAuthentication",
    "authorization.backends.RegularDatabaseAuthentication",
)


# ----------------------------------------- #
#                MISCELANEA                 #
# ----------------------------------------- #

# Forces the login form although the user has jwt on session (useful for dev envs)
FORCE_LOGIN_FORM = False

# Default theme for the login screens
WIGGUM_DEFAULT_THEME = "clancy"

# Wiggum allows multiple redirecting parameters. So will accept this parameters
# to redirect.
# Wiggum will use the first one to rewrite url parameters.
REDIRECT_URL_VALID_PARAMS = (
    "redirect_uri",  # Wiggum default one
    "next",          # Django auth/admin one
)

# The redirection webpage when the admin is not authorized
ADMIN_UNATHORIZED_REDIRECTION_URL = "/unauthorized/"

# The urls to apply the django session middleware based on jwt
JWT_SET_DJANGO_SESSION_URLS = (
    "/admin/.*",
)

# The urls wheren domain check middleware (WiggumValidCloneDomainMiddleware)
# doesn't apply
EXCLUDE_DOMAIN_CHECK_URLS = (
    "/api/.*",      # reverse("api:api-root")
    "/metrics/?",
    "/?$",
    "/robots.txt",
)
