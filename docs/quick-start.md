## Running on dev mode

As a quick-start we will run our project on local development mode.

First you will need to clone the wiggum project in a place where an application
will suited well (for example /opt)

```bash
cd /opt
git clone https://github.com/qdqmedia/wiggum.git wiggum
```

Edit your hosts files (`/etc/hosts`) so we set the JWT token for our fake domain

```
127.0.0.1       dev.login.wiggum.com
127.0.0.1       dev.login.wiggum.io
127.0.0.1       dev.login.wiggum.org
```

We are ready!

The prerequesites to run wiggum with docker is Make, [Docker] and [Docker compose]. Just do `make up` in projects root path. This will set you inside the project, run it on port `8009`

[Docker]: https://www.docker.com/
[Docker compose]: https://github.com/docker/compose

```
./manage.py runserver 0.0.0.0:8009
```

This will load dev settings by default

Go to [http://dev.login.wiggum.com:8009] and login with `admin` user and `admin` password
[http://dev.login.wiggum.com:8009]: http://dev.login.wiggum.com:8009

!!! info
    You need to have in mind that you are running this in dev mode and that you are
    using the default dev settings (keys and stuff)
