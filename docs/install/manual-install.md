
This is a common example to set up and running a personal Wiggum application. We
are assuming that we have these services.

```text
http://mycompany.io
http://documents.mycompany.io
http://backoffice.mycompany.com
http://deployments.mycompany.com
http://logs.mycompany.com
```

# Installation

We are setting on `/home/wiggumuser/apps` to do all the stuff.

## System dependencies

Wiggum is a Python3 application so you will need a python3 installation. Apart
from this, you will need some dependecies: `node`, `gettext`, `libffi`, `libssl` and `libpq`. In
apt based systems you will do:

```
# apt-get update
# apt-get install -y libffi-dev libssl-dev libpq-dev postgresql-client gettext node
```

## Database

We need a ready PostgreSQL with a database, user and stuff.

## JWT keys
We are going to use asymmetric keys this time, exactly we will use `RS256`
algorithm to sign the Token. We create the keys.

```bash
$ mkdir ./wiggum-keys && cd ./wiggum-keys
$ ssh-keygen  -t rsa -b 2048 -q -N "" -f ./wiggu
```

Now we have the private `wiggum` and the public `wiggum.pub` keys

!!! warning
    Private keys mean private! Don't share :)

## Get Wiggum

```bash
$ cd ..
$ git clone https://github.com/qdqmedia/wiggum.git
```

At this moment we have `wiggum` and `wiggum-keys` directories.

## App dependencies

We install the dependencies in the system or in a virtualenv, for this example we
will create a virtualenv named wiggumapp

```bash
$ mkvirtualenv wiggumapp
```

And install wiggum dependencies in this virtualenv

```bash
$ pip install -r ./wiggum/requirements/base.txt
```

Install node depdencies from wiggum project

```bash
$ cd ./wiggum
$ npm install
$ node_modules/.bin/bower install
```

## Create own settings

We need to create our own settings, we will set the least neccessary settings to
have a Personal wiggum app. We will create a directory where we will place all
of our custom configuration

```bash
$ cd -
$ mkdir ./wiggum-prod && ./wiggum-prod
$ touch ./conf.py
```

And start putting the settings on the `conf.py` file

### Import from base settings
Inherit from wiggum default settings

```python
import os
from wiggum.settings.wiggum import *
```

### Common Django stuff
We set the Django sessión key to a random hash and Debug to false

```python
SECRET_KEY = "32f&7^ih2&lc0&)enip3e_i^@8v2!(n1z4sx9fe@0shh2*e)=*"
DEBUG = False
```

The place the static and media files will be generated and placed

```python
MEDIA_ROOT = "/home/wiggumuser/media"
STATIC_ROOT = "/home/wiggumuser/static"
```

### Database & caches
Set the database settings to point to our postgres and use the local memory cache
Wiggum doesn't need to cache so we don't need something like Redis or memcached.

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('PG_DATABASE'),
        'USER': os.getenv('PG_USER'),
        'PASSWORD': os.getenv('PG_PASSWORD',),
        'HOST': os.getenv('PG_HOST', "127.0.0.1"),
        'PORT': os.getenv('PG_PORT', '5432'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'wiggum',
    }
}
```

### Static stuff

Wiggum uses [Django pipeline] to manage the assets so we need to point where
these binaries are

```python
PIPELINE_LESS_BINARY = os.path.join(NODE_MODULES_PATH, "less")
PIPELINE_UGLIFYJS_BINARY = os.path.join(NODE_MODULES_PATH, "uglifyjs")
PIPELINE_YUGLIFY_BINARY = os.path.join(NODE_MODULES_PATH, "yuglify")
```

### Wiggum

We set the issuer to our company wiggum and the name of the cookie

```python
JWT_ISSUER = "wiggum-mycompany"
JWT_COOKIE_NAME = "wiggum-mycompany"
```

Disable the transition keys, only need one key valid at a time.

```python
JWT_TRANSITION_ENABLE = False
```

As we saw at the beginning, we have apps on `mycompany.io` and `mycompany.com` domains
So we will need to clone the cookie. We are placing wiggum on `https://login.mycompany.com`
and `https://login.mycompany.io`, so this would use a level 2 autodomain:

```python
JWT_COOKIE_DOMAIN_AUTO = True
JWT_COOKIE_DOMAIN_AUTO_LEVEL = 2
JWT_COOKIE_CLONE = True
JWT_COOKIE_CLONE_DOMAINS_ENDPOINT = (
    "login.mycompany.io",
    "login.mycompany.com",
)
```

We set some default redirects.

```python
LOGIN_SUCCESS_REDIRECT = "http://mycompany.io"
LOGOUT_SUCCESS_REDIRECT = "/a/login"
```

Finally set the generated keys

First we set the content of the public key from `wiggum-keys/wiggum.pub`

```python
JWT_VERIFICATION_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCmFPuwTx+EsF5BOoFVqcVgDUdszogmk9yGsJFATdZZr3eYXIeZYJJOqOL2VZsepJfTjVJn6hNl57cpCjB39JpBja+GrSS1LRexIyPpyIkswhulSWOcb6rnIpIXuWpWXW/syT0jBOdRJZIH6HBIqC/et2IAoCtjHRZrsoympECQfk40tjUBctTv0RrmC8ouiWMyR67nhPJCcZFNVqtvR6BRrlg2iQOwj0h59/Z3hFNPZVPeAi0TwPDhs3HF3Gv/q84w5auFx7B3m32eHvMqzYVatUcRbkPskQVCh2Qbp2wFLraPaiHLHPXKMdVcUvoMpmjfi24HP6EeLBF2qy3kVWez wiggum@59448fc67e05"
```

Then the private key from `wiggum-keys/wiggum`

```python
JWT_SECRET_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAphT7sE8fhLBeQTqBVanFYA1HbM6IJpPchrCRQE3WWa93mFyH
mWCSTqji9lWbHqSX041SZ+oTZee3KQowd/SaQY2vhq0ktS0XsSMj6ciJLMIbpUlj
nG+q5yKSF7lqVl1v7Mk9IwTnUSWSB+hwSKgv3rdiAKArYx0Wa7KMpqRAkH5ONLY1
AXLU79Ea5gvKLoljMkeu54TyQnGRTVarb0egUa5YNokDsI9Ieff2d4RTT2VT3gIt
E8Dw4bNxxdxr/6vOMOWrhcewd5t9nh7zKs2FWrVHEW5D7JEFQodkG6dsBS62j2oh
yxz1yjHVXFL6DKZo34tuBz+hHiwRdqst5FVnswIDAQABAoIBAQCP3g9k3DWeWLVd
ZdPRo/4RRY+AxqwUVvOqTVuVy5eKG0DLYCQqjghPUWdCIkf8VHIc1Qf0ckWZeg8k
4um3j9DsRlMto+DvfP9P9/PNOWTyu7b9CETcp7LxA/ZvzLM72zbwdCacpkvG9He6
l/RkTCUjldG0XwsWkYTxiDrkw9YWE55Mbm/5dHPGj75oaJZWhJRPV/g0S+okKLlR
7y/uBB8ZgmdobTkN0XkR2vjLtCr8u+y4GPVcO/9JdjPsXxZbDD4GosAWoTR2oVR9
/MnbtwoECf0aVb22LAuE0wIrTIXIFIj+/I5/K7gan/6RucM2nqZq/og8iH9Kjnba
eu8ZqOXRAoGBANNeNzVnKMyS3S2wPjY6BMiLdEPhWJgtdw+t/b01c1Cq52aEYh0X
vcO6AqdERxH6IKF/fnOJ1bf5JeiZdZKDChfRlwhGylw7duNxe5JMw3DG/y7BgxFT
7P7AO0X4IKmhROS0+cPfVD/DxRiC183IBmZdrDB+PTy1vAIB1e4vXv8ZAoGBAMkm
xKORRMF1Rh5aMYdZ3tGe9K5XyY8m73Onb1MYMaP5LuFgmiTYAED//aF04cjYBY4L
3BZ638HXc4PiyonzTlD1Ks/rHUudIqmk/chM6BXsyMyROCGgw13kQq4A5omWfkWC
16kGgDxQ+1hHZRmWsPOD7bNnl3++TR/oHq9341KrAoGATHcwJ9yrEN8sruOsjfeN
VXPF2uzCHUONaBm8yt90WUGKtza7O+Uj3JQFc7eqsmE3vtUdzPSXYZf709r4gslv
NFC5f+AEQzur9fpPBw1IQxtqo+KT5QfknAC1MMnkHxndj5O9K9Q2aV8MhaKIKcTs
M8o9icmRo83nNx6s4x82EbkCgYAKqm6UybgelexQ4bFsntxMuyP4NpluaL8bn84s
VsUTD7xnoOqrd3ST/b7iF8N9Fc89l+1kl8FTkuwCGz1oESme61EI00urXbqfyirW
uxU3TGXdSvnx9odFbDwI4+1VcFBjuStcQAb+q8CYDrkSoUXis6Uf9Sc4U8vdHD68
SRwZnwKBgEb9WeG2faQ2z/yVS/GackxoOu1Iuva2Mm6iRjW5RN+aKoz9j1S/1///
baIuTGlMpuHGwD+E8t1OPZ4ePCtHBKBogNefwBt+2bB40nZTzON+SX2JgdOEmo8z
DryNZ5s3VOt7bQrz97xSM8II7JuUVHCf5vB1DXGeDVccY2N+Bj+6
-----END RSA PRIVATE KEY-----"""
```

The sign algorithm and verification one, they are the same

```python
JWT_SIGN_ALGORITHM = "RS256"
JWT_SIGN_VALID_ALGORITHMS =[JWT_SIGN_ALGORITHM, ]
```

### Allowed hosts

We said that wiggum will be on `https://login.mycompany.com`
and `https://login.mycompany.io`, we enable seving on this hosts:

```python
ALLOWED_HOSTS = [
                 "login.mycompany.com",
                 "login.mycompany.io",
                 "127.0.0.1",
                 "localhost"]
```


### All in one file

This is the result of our configuration
```python
import os
from wiggum.settings.wiggum import *


SECRET_KEY = "32f&7^ih2&lc0&)enip3e_i^@8v2!(n1z4sx9fe@0shh2*e)=*"
DEBUG = False

MEDIA_ROOT = "/media"
STATIC_ROOT = "/static"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('PG_DATABASE'),
        'USER': os.getenv('PG_USER'),
        'PASSWORD': os.getenv('PG_PASSWORD',),
        'HOST': os.getenv('PG_HOST', "127.0.0.1"),
        'PORT': os.getenv('PG_PORT', '5432'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'wiggum',
    }
}

PIPELINE_LESS_BINARY = os.path.join(NODE_MODULES_PATH, "less")
PIPELINE_UGLIFYJS_BINARY = os.path.join(NODE_MODULES_PATH, "uglifyjs")
PIPELINE_YUGLIFY_BINARY = os.path.join(NODE_MODULES_PATH, "yuglify")

JWT_ISSUER = "wiggum-mycompany"
JWT_COOKIE_NAME = "wiggum-mycompany"
JWT_TRANSITION_ENABLE = False
JWT_COOKIE_DOMAIN_AUTO = True
JWT_COOKIE_DOMAIN_AUTO_LEVEL = 2
JWT_COOKIE_CLONE = True
JWT_COOKIE_CLONE_DOMAINS_ENDPOINT = (
    "login.mycompany.io",
    "login.mycompany.com",
)

LOGIN_SUCCESS_REDIRECT = "http://mycompany.io"
LOGOUT_SUCCESS_REDIRECT = "/a/login"

JWT_VERIFICATION_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCmFPuwTx+EsF5BOoFVqcVgDUdszogmk9yGsJFATdZZr3eYXIeZYJJOqOL2VZsepJfTjVJn6hNl57cpCjB39JpBja+GrSS1LRexIyPpyIkswhulSWOcb6rnIpIXuWpWXW/syT0jBOdRJZIH6HBIqC/et2IAoCtjHRZrsoympECQfk40tjUBctTv0RrmC8ouiWMyR67nhPJCcZFNVqtvR6BRrlg2iQOwj0h59/Z3hFNPZVPeAi0TwPDhs3HF3Gv/q84w5auFx7B3m32eHvMqzYVatUcRbkPskQVCh2Qbp2wFLraPaiHLHPXKMdVcUvoMpmjfi24HP6EeLBF2qy3kVWez wiggum@59448fc67e05"
JWT_SECRET_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAphT7sE8fhLBeQTqBVanFYA1HbM6IJpPchrCRQE3WWa93mFyH
mWCSTqji9lWbHqSX041SZ+oTZee3KQowd/SaQY2vhq0ktS0XsSMj6ciJLMIbpUlj
nG+q5yKSF7lqVl1v7Mk9IwTnUSWSB+hwSKgv3rdiAKArYx0Wa7KMpqRAkH5ONLY1
AXLU79Ea5gvKLoljMkeu54TyQnGRTVarb0egUa5YNokDsI9Ieff2d4RTT2VT3gIt
E8Dw4bNxxdxr/6vOMOWrhcewd5t9nh7zKs2FWrVHEW5D7JEFQodkG6dsBS62j2oh
yxz1yjHVXFL6DKZo34tuBz+hHiwRdqst5FVnswIDAQABAoIBAQCP3g9k3DWeWLVd
ZdPRo/4RRY+AxqwUVvOqTVuVy5eKG0DLYCQqjghPUWdCIkf8VHIc1Qf0ckWZeg8k
4um3j9DsRlMto+DvfP9P9/PNOWTyu7b9CETcp7LxA/ZvzLM72zbwdCacpkvG9He6
l/RkTCUjldG0XwsWkYTxiDrkw9YWE55Mbm/5dHPGj75oaJZWhJRPV/g0S+okKLlR
7y/uBB8ZgmdobTkN0XkR2vjLtCr8u+y4GPVcO/9JdjPsXxZbDD4GosAWoTR2oVR9
/MnbtwoECf0aVb22LAuE0wIrTIXIFIj+/I5/K7gan/6RucM2nqZq/og8iH9Kjnba
eu8ZqOXRAoGBANNeNzVnKMyS3S2wPjY6BMiLdEPhWJgtdw+t/b01c1Cq52aEYh0X
vcO6AqdERxH6IKF/fnOJ1bf5JeiZdZKDChfRlwhGylw7duNxe5JMw3DG/y7BgxFT
7P7AO0X4IKmhROS0+cPfVD/DxRiC183IBmZdrDB+PTy1vAIB1e4vXv8ZAoGBAMkm
xKORRMF1Rh5aMYdZ3tGe9K5XyY8m73Onb1MYMaP5LuFgmiTYAED//aF04cjYBY4L
3BZ638HXc4PiyonzTlD1Ks/rHUudIqmk/chM6BXsyMyROCGgw13kQq4A5omWfkWC
16kGgDxQ+1hHZRmWsPOD7bNnl3++TR/oHq9341KrAoGATHcwJ9yrEN8sruOsjfeN
VXPF2uzCHUONaBm8yt90WUGKtza7O+Uj3JQFc7eqsmE3vtUdzPSXYZf709r4gslv
NFC5f+AEQzur9fpPBw1IQxtqo+KT5QfknAC1MMnkHxndj5O9K9Q2aV8MhaKIKcTs
M8o9icmRo83nNx6s4x82EbkCgYAKqm6UybgelexQ4bFsntxMuyP4NpluaL8bn84s
VsUTD7xnoOqrd3ST/b7iF8N9Fc89l+1kl8FTkuwCGz1oESme61EI00urXbqfyirW
uxU3TGXdSvnx9odFbDwI4+1VcFBjuStcQAb+q8CYDrkSoUXis6Uf9Sc4U8vdHD68
SRwZnwKBgEb9WeG2faQ2z/yVS/GackxoOu1Iuva2Mm6iRjW5RN+aKoz9j1S/1///
baIuTGlMpuHGwD+E8t1OPZ4ePCtHBKBogNefwBt+2bB40nZTzON+SX2JgdOEmo8z
DryNZ5s3VOt7bQrz97xSM8II7JuUVHCf5vB1DXGeDVccY2N+Bj+6
-----END RSA PRIVATE KEY-----"""

JWT_SIGN_ALGORITHM = "RS256"
JWT_SIGN_VALID_ALGORITHMS =[JWT_SIGN_ALGORITHM, ]

ALLOWED_HOSTS = [
                 "login.mycompany.com",
                 "login.mycompany.io",
                 "127.0.0.1",
                 "localhost"]
```

# Python path

we are using `django-admin` command, to get this command working we will need to
add wiggum project path and configuration path to the `PYTHONPATH`

```bash
export PYTHONPATH=$PYTHONPATH:/home/wiggumuser/apps/wiggum-prod:/home/wiggumuser/apps/wiggum/wiggum
```

# Migrations and admin user

Apply database migrations.

```bash
$ django-admin migrate --settings="conf"
```

Create the admin user

```bash
$ django-admin createsuperuser --settings="conf"
```

# Generate statics and translations

Generate statics

```bash
$ mkdir /home/wiggumuser/static
$ mkdir /home/wiggumuser/media
$ django-admin collectstatic --settings="conf"
```

Generate  translations
The translations are placed by default in wiggum project root in `locale` directory
this would be: `/home/wiggumuser/wiggum/wiggum/locale`

```bash
$ mkdir -p home/wiggumuser/wiggum/wiggum/locale
$ django-admin compilemessages --settings="conf"
```

# uwsgi

We are using [uwsgi] to run wiggum, and [whitenoise] to serve the few statics from uwsgi,
this could be done with an Nginx, but this is out of the scope. Install both dependencies
[uwsgi]: https://uwsgi-docs.readthedocs.org/en/latest/
[whitenoise]: https://github.com/evansd/whitenoise

```bash
$ pip install uwsgi whitenoise
```

We create the Django wsgi module in `/home/wiggumuser/apps/wiggum-prod`

```bash
$ touch /home/wiggumuser/apps/wiggum-prod/wsgi.py
```

with the content
```python
from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

application = get_wsgi_application()

application = DjangoWhiteNoise(application)

```


We create a uwsgi.ini in `/home/wiggumuser/apps/wiggum-prod` file with the configuration

```ini
[uwsgi]
pythonpath = "/home/wiggumuser/apps/wiggum-prod:/home/wiggumuser/apps/wiggum/wiggum"
http = 0.0.0.0:8000
module = wsgi
stats = /tmp/uwsig_stats.socket

# Delete all sockets created
vacuum = true

# Do not let block our process if an external service is taking to much time
harakiri = 10
```


Lets run wiggum!

```bash
DJANGO_SETTINGS_MODULE="conf" uwsgi --ini /home/wiggumuser/apps/wiggum-prod/uwsgi.ini
```

!!! warning
    You should set HAProxy, Nginx or similar in front of the uwsgi, but again this is out of the scope

!!! warning
    Wiggum always uses https, if `DEBUG=True` http is enabled. To keep things simple I
    would suggest setting an HAProxy or similar in front of wiggum to handle the
    TLS connection.
