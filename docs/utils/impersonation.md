Wiggum has the ability to impersonate a user. This is to act as an specific user
without being that user.

# Impersonate

This is useful when you want to debug, how an application acts being a specific
user to fix bugs and  stuff. To impersoante an user you will need to be logged
already in wigum and have `wiggum.impersonate` permission, *with great power comes
great responsibility*.

You can impersonate a user using `a/impersonate/{ID}`. One impersoante an special
JWT token will replace your existing token.

In the admin panel each user has an impersonate button in his/her details to
help impersonating this user in an easy way.

# Impersonate token

```javascript
{
  "real_user_id": 1,
  "impersonate": true,
  "iss": "wiggum",
  "nbf": 1457344554,
  "iat": 1457344569,
  "user": {
    "username": "xilarrakoetxea",
    "last_name": "Larrakoetxea Gallego",
    "id": 7052,
    "email": "xilarrakoetxea@qdqmedia.com",
    "first_name": "Xabier Iñigo"
  },
  "version": 1.1,
  "exp": 1457348169
}
```

When impersonating the JWT token will be the same as if the impersoante user was
logged, but also will have `"impersonate": true` & `"real_user_id": "XX"` with the
ID of the user that impersonated the actual user. As a security, the impersonated
Tokens will expire in less time that regular ones. by default expire in `1h`, you
can change this with `JWT_IMPERSONATE_EXPIRATION_TIME_DELTA` setting.



!!! note
    Impersonating destroys the current session.
