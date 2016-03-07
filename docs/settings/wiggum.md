Settings in Wiggum use the default Django system settings, this is a python file.
with key-values. Settings can inherit from other settings and thats how we would
extend wiggum as you will see in the [customization section]

The main wiggum settings are in [wiggum.py].

[customization section]: ../custom/introduction.md
[wiggum.py]: ../wiggum/wiggum/settings/wiggum.py


# JWT authorization settings
In these settings are the common security settings as keys and algorithms to
sign the JWT token.


## JWT_SECRET_KEY
This is the key used to sign the JWT token. This needs to be a valid & supported key
for the JWT stardard supported algorithms, check [PyJWT] library for the supported ones.
[PyJWT]: http://pyjwt.readthedocs.org/en/latest/algorithms.html#digital-signature-algorithms

The algorithms can be of two types, symmetric and asymmetric, for the first one theres only one key, so this key will be place it here. In case of using an asymmetric one there will be 2 keys and here will be placed the private key.


!!! note
    This can be set with `JWT_SECRET_KEY` env var

!!! warning
    This key is secret! don't share with anybody

## JWT_VERIFICATION_KEY
This is the key used to verificate signed JWT tokens. As with `JWT_SECRET_KEY` this key
needs to be a valid ans supported key by the standard. In case a symmetric key is used
then this will be set to the same key as the JWT_SECRET_KEY, in case of using asymmetric
keys then this will be set with the public key

!!! note
    This can be set with `JWT_VERIFICATION_KEY` env var

## JWT_SIGN_ALGORITHM
This will be the algorithm used to sign the JWT token, Could be asymmetric or symmetric.

!!! note
    Default to symmetric algorithm `HS256`

!!! note
    This can be set with `JWT_SIGN_ALGORITHM` env var

!!! warning
    This setting needs valid `JWT_SECRET_KEY` & `JWT_VERIFICATION_KEY`



## JWT_TRANSITION_ENABLE
This setting (True/False) enables a second verification key for JWT tokens (usually an old key).
This is used because when we change our singing keys sometimes the old keys need to
be valid on little period of time while the transition occurs.

!!! note
    Default deactivated

!!! note
    This can be activated  settin `JWT_TRANSITION_ENABLE` env var to one of this: `True`, `true`, `Yes`, `yes`, or `y`

## JWT_TRANSITION_VERIFICATION_KEY
Applies the same as `JWT_VERIFICATION_KEY` but for the transition verification key

!!! note
    This can be set with `JWT_TRANSITION_VERIFICATION_KEY` env var


## JWT_SIGN_VALID_ALGORITHMS
An array of the valid algorithms in order to check the JWT tokens with the keys.
The algorithms need to be JWT standard valid ones.

!!! note
    This can be set with `JWT_SIGN_VALID_ALGORITHMS` env var, the values are set
    space separated, for example: `JWT_SIGN_VALID_ALGORITHMS="HS256 RS256"`

!!! note
    Default valid algorithms are `HS256` & `RS256`


## JWT_EXPIRATION_TIME_DELTA
An integer that describes the maximum time (in seconds) a token will be valid
after creating it

!!! note
    Default to 15 days

## JWT_NBF_LEEWAY_SECONDS
An integer that describes the maximum time (in seconds) a token creation time
can be valid. Used normally when multiple instances of wiggum are deployed and
They have small time offset making the token to be invalid when a machine created the token and then is validated in another machine with the timestamp in the future making
the token creation timestamp be in the future. Used by JWT `ǸBF` attribute

!!! note
    Default to 15 seconds

## JWT_ISSUER

An string that describes the issuer of the JWT token. Used by JWT `ìss` attribute

!!! note
    Default to `wiggumio`

!! note
    This can be set with `JWT_ISSUER` env var


# JWT cookie settings
These settings are the ones that will determine how the JWT cookie is created and
set.


## JWT_COOKIE_NAME
An string with the name of the cookie

!!! note
    Default to `wiggumio_jwt`

## JWT_COOKIE_EXPIRATION_TIME_DELTA
The time in seconds where the cookie will be valid. Usually this is set to the
same time as the `JWT_EXPIRATION_TIME_DELTA`

!!! note
    Default to same as `JWT_EXPIRATION_TIME_DELTA`

## JWT_COOKIE_ONLY_HTTPS
A boolean value, if enabled the cookie that is set will only be valid in https

!!! note
    Deactivated by default

!!! warning
    If active be sure that all the applications using wiggum generated cookies are in HTTPS

## JWT_COOKIE_DOMAIN
The domain/subdomain/domain-wilcard  where the cookie will be sent.

!!! note
    Default to `.wiggum.io`

!!! note
    This setting usually isn't used in favor of `JWT_COOKIE_DOMAIN_AUTO`, this last setting has priority

## JWT_COOKIE_DOMAIN_AUTO
A boolean value that if is enabled will set the cookie valid for the domain/subdomain/wildcard where wiggum is listening.

!!! note
    Active by default

!!! note
    The way the domain/subdomain/wildcard is obtained is based on `JWT_COOKIE_DOMAIN_AUTO_LEVEL`

## JWT_COOKIE_DOMAIN_AUTO_LEVEL
An integer value specifying the level of the domain that will be obtained where
wiggum is listening based on the request. For example.

User request from: `login.production.wiggum.org`

- level 2 : `.wiggum.org`
- level 3: `.production.wiggum.org`

User request from: login.staging.wiggum2.com

- level 4: `.login.staging.wiggum2.com`

!!! note
    If level is less or equal to `1` then the domain will be the request domain

!!! note
    Default value to `2`

## JWT_COOKIE_CLONE
A boolean value. If activated then cloning the cookie is allowed to wiggum. This
works by cloning the cookie to a list of described domains when the user logs in.

For example if we have  3 applications that need to authenticate with wiggum token:

* app1.company.org
* app2.company.com
* app3.comp.com

Wiggum should set the cookie on the `.company.org`, `.company.com` and `.comp.com`
domains, this is done by cloning the cookie.

!!! note
    Activated by default

!!! note
    This can be activated  settin `JWT_COOKIE_CLONE` env var to one of this: `True`, `true`, `Yes`, `yes`, or `y`


!!! warning
    To use the cookie cloning mechanism you should use `JWT_COOKIE_CLONE_DOMAINS_ENDPOINT`, `JWT_COOKIE_DOMAIN_AUTO` & `JWT_COOKIE_DOMAIN_AUTO_LEVEL`

## JWT_COOKIE_CLONE_DOMAINS_ENDPOINT
A list of strings containing the clone domains where wiggum is listening. Taking
`JWT_COOKIE_CLONE` example. We should set wiggum listening on these domains (can be the same wiggum instance, and point all these domains to the same one):

```python
JWT_COOKIE_CLONE_DOMAINS_ENDPOINT = (
    "login.company.org",
    "login.company.com",
    "login.comp.com",
)
```


## JWT_SET_PERMISSION_ON_TOKEN
A boolean value that sets the permissions of a user on the token. This is useful
when you don't want to check by API each user authorization.

!!! warning
    If you need real time permissions check you should avoid using this and check in wiggum (by API) each time you want to know a users permissions.

!!! note
    Deactivated by default

## JWT_VERSION
A float setting that will be set on each JWT token generation. Useful to identify
the version of the JWT issued token. Useful when an JWT is updated with new or
modified content.

!!! note
    The default & initial version is `1.1`

## JWT_MINIMUM_VERSION
A float settings that will specify which versión on JWT tokens are valid or invalid,
for example a 1.4 versioned JWT and a 1.5 of minimim JWT version, when validated on wiggum will be identify as an invalid token

!!! note
    The default minimum version is `1`

## JWT_DESTROY_TOKEN_ON_LESSER_VERSION
A boolean value than specifies if the action to be done on not version valid tokens
need to be deleted from the client

!!! note
    Activated by default

# JWT miscelanea settings

These settings don't alow to any type of JWT group of settings

## JWT_IMPERSONATE_ENABLE
A boolean value that specifies if wiggum should allow impersonating users. Check
[impersonation] section to understand how it works.

[impersonation]: utils/impersonation

!!! note
    Activated by default

## JWT_IMPERSONATE_EXPIRATION_TIME_DELTA
An integer value specifying the number of seconds the JWT impersonated token is valid

!!! note
    Default to `1 hour`

## JWT_IMPERSONATE_COOKIE_EXPIRATION_TIME_DELTA
An integer value specifying the number of seconds the cookie is valid

!!! note
    Default to `JWT_IMPERSONATE_EXPIRATION_TIME_DELTA` value


## JWT_SFA_ENABLE
A boolean value that specifies if wigum should allow SFA logins. Check [SFA] section
for more information

[SFA]: utils/SFA

!!! note
    Activated by default

## JWT_SFA_EXPIRE_DELTA
An integer value specifying the number of seconds the SFA token (link) will be valid

!!! note
    Default to `1 hour`


# App permission settings
Settings for authorization  stuff

## APP_PERMISSION_KEYS
A dictionary/map of settings specifying the application used permissions.

!!! note
    Default defined permissions `wiggum.all` & `wiggum.impersonate`

!!! warning
    This shouldn't be changed

# API settings
API settings, no more no less

## API_VERSION
A string defining the api prefix version.

!!! note
    Default to "v1"

!!! warning
    This shouldn't be changed

# Action settings

Action settings specify the flow of actions for each of the events that occur.
Check [actions] section to learn more about Wiggum actions

[actions]: customization/actions

## LOGIN_PRE_CHECK
List of actions that occur when a login is submitted and checked.

!!! note
    Default action flow:

    "authorization.actions.login_pre_check.ForceLoginFormAction",
    "authorization.actions.login_pre_check.CheckUserAuthenticatedAlreadyAction",
    "authorization.actions.login_pre_check.CheckValidJWTVersionAction",

## LOGIN_SUCCESS_ACTIONS
List of actions that occur when a login succeeds.

!!! note
    Default action flow:

    "authorization.actions.login_success.CreateJWTAction",
    "authorization.actions.login_success.RedirectToCloneJWTSessionAction",
    "authorization.actions.login_success.SetJWTOnCookieAction",
    "authorization.actions.login_success.LoginSuccessMetricAction",


## LOGIN_FAILURE_ACTIONS
List of actions that occur when a login fails

!!! note
    Default action flow:

    "authorization.actions.login_failure.AuthenticationErrorMessageAction",
    "authorization.actions.login_failure.LoginFailureMetricAction",

## LOGOUT_ACTIONS
List of actions that occur when a logout is done.

!!! note
    Default action flow:

    "authorization.actions.logout.DeleteDjangoAuthSessionAction",
    "authorization.actions.logout.JWTDeleteCookieAction",
    "authorization.actions.logout.LogoutMetricsAction",

## CLONE_ACTIONS
List of actions that occur when a cookie clone is done.

!!! note
    Default action flow:

    "authorization.actions.login_success.SetJWTOnCookieAction",

## RECOVER_PASS_REQUEST_ACTIONS
List of actions that occur when a password recover request is done.

!!! note
    Default action flow:

    "authorization.actions.recover_pass_request.LoadUserFromDatabaseAction",
    "authorization.actions.recover_pass_request.CheckUserCorrectAction",
    "authorization.actions.recover_pass_request.CreateRecoverPasswordTokenAction",
    "authorization.actions.recover_pass_request.PasswordResetRequestMetricAction",

## RESET_PASS_ACTIONS
List of actions that occur when a password recover is done.

!!! note
    Default action flow:

    "authorization.actions.reset_pass.CreateJwtOnViewOnPassResetAction",
    "authorization.actions.reset_pass.RedirectToCloneJWTSessionOnPassResetAction",
    "authorization.actions.reset_pass.SetJWTOnCookieOnPassResetAction",
    "authorization.actions.reset_pass.PasswordResetMetricAction",

## IMPERSONATE_ACTIONS
List of actions that occur when a user impersonation occurs.

!!! note
    Default action flow:

    "authorization.actions.impersonate.CheckImpersonateActiveAction",
    "authorization.actions.impersonate.RedirectToLoginIfNotAuthenticatedAction",
    "authorization.actions.login_pre_check.CheckValidJWTVersionAction",
    "authorization.actions.impersonate.CheckImpersonatePermissionAction",
    "authorization.actions.impersonate.CheckImpersonateSameUserAction",
    "authorization.actions.impersonate.CreateImpersonateJWTAction",
    "authorization.actions.login_success.RedirectToCloneJWTSessionAction",
    "authorization.actions.impersonate.SetImpersonateJWTOnCookieAction",
    "authorization.actions.impersonate.ImpersonationMetricAction",

## SFA_ACTIONS
List of actions that occur when a SFA login occurs.

!!! note
    Default action flow:

    "authorization.actions.sfa.CheckSFAActiveAction",
    "authorization.actions.login_success.CreateJWTAction",
    "authorization.actions.login_success.RedirectToCloneJWTSessionAction",
    "authorization.actions.login_success.SetJWTOnCookieAction",
    "authorization.actions.sfa.ResetSFATokenAction",

# Default redirections settings
Default redirections are the urls where the user will be redirected after the
action was successfully finished

## LOGIN_SUCCESS_REDIRECT
Default url where the user will be redirected after successful login

!!! note
    Default to `/a/test/jwt`

## LOGOUT_SUCCESS_REDIRECT
Default url where the user will be redirected after successful logout

!!! note
    Default to `/a/test/jwt`

## CLONE_SUCCESS_REDIRECT
Default url where the user will be redirected after successful final clone chain

!!! note
    Default to `/a/test/jwt`

## RECOVER_PASS_REQUEST_SUCCESS_REDIRECT
Default url where the user will be redirected after successful password reset request

!!! note
    Default to `/a/login`

## RESET_PASS_SUCCESS_REDIRECT
Default url where the user will be redirected after successful password reset

!!! note
    Default to `/a/login`

## IMPERSONATE_SUCCESS_REDIRECT
Default url where the user will be redirected after successful impersonation

!!! note
    Default to `/a/test/jwt`

## SFA_SUCCESS_REDIRECT
Default url where the user will be redirected after successful SFA login

!!! note
    Default to `/a/login`

#  Password reset settings
Settings related with the password reset

## PASSWORD_RESET_EXPIRE_DELTA
Integer value expressed in seconds that specifies how long the reset password
link will be valid

!!!note
    Default value is `12 hours`

## LOGIN_ON_PASSWORD_RESET
Boolean value that specifies if the user needs to be logged-in after a password reset

!!!note
    Activated by default

# Authentication backends settings
Settings related with wiggu authentication system

## WIGGUM_AUTHENTICATION_BACKENDS
A list specifying the authentication backends used by wiggum to login the user
on wiggum appplication.

!!! note
    Default:

    "authorization.backends.JWTAuthentication",
    "authorization.backends.RegularDatabaseAuthentication",
)

# Miscelanea settings
Settings that don't fit in any section

## FORCE_LOGIN_FORM
A boolean value that specifies if wiggum should ask for the login form always. Useful when developing

!!! note
    Deactivated by default

## WIGGUM_DEFAULT_THEME
A setting specifying the theme that will be loaded by default

!!! note
    Default theme is `clancy`

## REDIRECT_URL_VALID_PARAMS
A list that specifies the valid querystring for url redirect forcing. For example
when we want to redirect to `mysite.com/something` after a successful login we
could use `wiggum.io/login?redirect_uri=mysite.com/something`

!!! note
    Default ones are `next` & `redirect_uri`

## ADMIN_UNATHORIZED_REDIRECTION_URL
A string specifying the url that will be a user redirected when tries to access
wiggum admin panel and that used doesn't have permissions to enter.

!!! note
    Default to `/unauthorized/`

## JWT_SET_DJANGO_SESSION_URLS
A list containing the urls regexes where the Django session middleware will be applied

!!! note
    Default to `/admin/.*`

## EXCLUDE_DOMAIN_CHECK_URLS
Wiggum checks if the domain where the request is accessing is a valid one (this
valid domains are the ones that appear on `JWT_COOKIE_CLONE_DOMAINS_ENDPOINT`)
This setting is a list of regexes.

!!! note
    Only applied when `JWT_COOKIE_CLONE` is enabled

!!! note
    Default ones:`/api/.*`, `/metrics/?`, `/?$` and `/robots.txt`
