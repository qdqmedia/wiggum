> *Authorization or authorisation is the function of specifying access rights to resources related to information security and computer security in general and to access control in particular*

> From the [wikipedia]

[wikipedia]: https://en.wikipedia.org/wiki/Authorization

# Check User permissions

User permissions or rights are managed with a list of dot notation strings, as
is explained in the [introduction]

[introduction]: introduction

To check user permissions you will need to check the [API]. In this example
we request permissions for user with ID 1 in `api/v1/users/1/`, as you see,
`project_permissions` is an array of permissions:

```javascript
{
    "id": 1,
    "project_permissions": [
        "cms.user",
        "landerdash.all",
        "landerdash.manage.any",
        "landerdash.manage.own",
        "ldap.user",
        "backoffice.user",
        "lander.editor",
        "lander.admin",
        "wiggum.impersonate",
        "wiggum.all"
    ],
    "last_login": "2016-03-04T08:45:16.197905Z",
    "username": "slok",
    "email": "slok69@gmail.com",
    "first_name": "Xabier",
    "last_name": "Larrakoetxea",
    "date_joined": "2015-07-22T14:54:43Z",
    "active": true,
    "external_service": ""
}
```

[API]: utils/api

!!! note
    Before checking user permissions, you should check that the user is
    authenticated, this means that has a valid wiggum token
