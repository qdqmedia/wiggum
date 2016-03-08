# Flow
Wiggum has a simple objective, the flow is very easy to understand as you see
in this image, the user logins on wiggum and then a cookie is set to that user
for a domain or wildcard domain. Now the user has a valid JWT token that
applications can check if the user is authenticated. So the user authentication
is stateless


![Wiggum flow](img/wiggum.png)


When wiggum authenticates a user the applications that use wiggum as a login system
must trust wiggum, this means that if a user has a wiggum JWT valid token, we can say
that the user is logged in.


# Users

Wiggum login is based on users, to be more exact, wiggum has a model named `User`
The user has very few attributes:

* ID: A wiggum ID (unique) (must)
* Username: A user username (unique) (must)
* email: A user email (unique) (must)
* First name: A user first name (not needed)
* Last name: A user last name (not needed)
* Password: The user password (must)

You can create a new user with the [admin] panel that wiggum has or with the
wiggum [API]

[admin] utils/admin
[API] utils/api

# Permissions
Permissions are linked with the User model, ths model specifies what are the user
rights.

Sometimes may only be needed that the user is authenticated, but other times we
need to difference an user from other user. The system used in Wiggum is simple,
a right or permission is a simple string. Usually with dotted notation. For example:

```
backoffice.user
backoffice.editor
wiggum.all
wiggum.impersonate
photos.production.editor
photos.internal.admin
```

A user has a list of permission linked to it.

# Apps

Apps are mainly used to use the API, it has nothing to do with . Apps have a token linked to it, this token is used as the API authentication mechanism.


# Wiggum philosophy

Many people can be tempted to start adding stuff to the user model, but this is
wrong. Wiggum is only an auth system, Wiggum doesn't need to know anything else
about the user, so, your user profile should reside in a centralized app, in
multiple apps... depends on the architecture that you have.

In order to link in a way the wiggum user and the user information (profile) of
other applications, you will need to use one of the unique fields that wiggum users
have: `email` or `username`

# Wiggum token

The signed wiggum token is a standard JWT


```
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2ZXJzaW9uIjoxLjEsImlzcyI6IndpZ2d1bS1iZXRhIiwiZXhwIjoxNDU3MjgwNDg3LCJuYmYiOjE0NTcwMjEyNzIsInVzZXIiOnsidXNlcm5hbWUiOiJzbG9rIiwiZW1haWwiOiJzbG9rNjlAZ21haWwuY29tIiwiaWQiOjEsImZpcnN0X25hbWUiOiJYYWJpZXIiLCJsYXN0X25hbWUiOiJMYXJyYWtvZXR4ZWEifSwiaWF0IjoxNDU3MDIxMjg3fQ.RrU09evYLEXvMbLqSzsbA4EqCnYH4PFQy3Jlm6MRNelIam_oEVMn5qpcQHcno9RhqL4wO6BrTu6gHPfjnZzmPA6k5RX8fQE3pdN1yfwWiLJFQ4vPTcYcV2wr24xJ7Ye8H3OVdoMkhn98M1lgQ-UcFoNMkWsDhgn8-k31IamhO6yrvEjj_l1-CWIeUBJ_Q5tCRHea0QW3mIkXCtAhjhUhp0ZnNGo52fmc2X7NqKiKJMjSYYh7DH-skd_hUtE4PiFZfHwgbvb49CiKx0PEd4vyEqpf1qiMpkT-wRVIKzFmxoQ-qiW8Dedb4WNBjGKvXWshd21VuctshpdcVbpPLnJG1A
```

Decoded

```javascript
{
    "version": 1.1,
    "iss": "wiggum-beta",
    "exp": 1457280487,
    "nbf": 1457021272,
    "user": {
        "username": "slok",
        "email": "slok69@gmail.com",
        "id": 1,
        "first_name": "Xabier",
        "last_name": "Larrakoetxea"
    },
    "iat": 1457021287
}
```

This object above will be the source of information the apps that trust wiggum will
use to obtain the logged user

# Applications

Once the cookie with the JWT token is on users browser, the cookie will be
attached on each request, this stateless authentication system makes that applications
don't need to maintain anything about user authentication in its session.

With the JWT cookie on users session is job of the application to check the
cookie token signature and the user permissions so it can deny the access to the user or not,
We will see this in an [example]

[example]: example
