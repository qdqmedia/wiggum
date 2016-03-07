Wiggum has a simple but powerful JSON API to get the information, about users,
permissions and applications.

# Documentation

You can read all the API documentation on `/api/v1` url. Needs authorization, read the next section.

# Authorization
you will need to set the `Authorization` header in order to use the API. To do that first you need to
enter on the admin panel `/admin`, create a new application and there generate a
token. Now you can authorize API calls using `Authorization: Bearer {TOKEN}` header

```bash
curl -H "Content-Type: application/json" -H "Authorization: Bearer f3d3a3f40e054c3b979f1dbceb05a712" http://xxxxxxxx.com/api/v1/users/1/
{"id":1,"project_permissions":["cms.user","wiggum.impersonate","landerdash.all","landerdash.manage.any","landerdash.manage.own","ldap.user","backoffice.user","lander.editor","lander.admin","wiggum.user.read","wiggum.user.write","wiggum.permission.write","wiggum.all"],"last_login":"2016-03-04T08:45:16.197905Z","username":"slok","email":"slok69@gmail.com","first_name":"Xabier","last_name":"Larrakoetxea","date_joined":"2015-07-22T14:54:43Z","active":true,"external_service":""}
```

# Endpoints

The main endpoints for resuources are:

- `/api/v1/users`: User model API endpoint
- `/api/v1/usernames`: Same as user, using usernames as user ID instead
- `/api/v1/applications`: Application model API enpoint
- `/api/v1/permissions`: Permissions model API endpoint

these endpoints allow to create, update, delete and retrieve data from each resource

# Special actions

Wiggum has some special actions on the API appart fro the regular resource API.

- `/api/v1/users/{ID}/reset-password-url?expiration_seconds=XXX`: Will get a link to reset the password of a user with a valid time of `expiration_seconds` querystring
- `/api/v1/users/{ID}/reset-password-url?expiration_seconds=XXX`: Same as above but with username as ID
- `/api/v1/usernames/{username}/sfa_url?expiration_seconds=XXX`: Will get a link to login with SFA mode, the link will be valid for the `expiration_seconds` querystring seconds
- `/api/v1/usernames/{username}/sfa_url?expiration_seconds=XXX`: Same as above but with username as ID

- `/api/v1/applications/{ID}/reset_token`: Resets application authorization token
