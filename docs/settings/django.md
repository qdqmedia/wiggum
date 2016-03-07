This will be the description of django main settings that need to be edited
in order to run the project. You can check [wiggum django settings] and [Django docs] in order to change
other common Django settings not listed in this document.

[wiggum django settings]: [base.py]: ../wiggum/wiggum/settings/base.py
[Django docs]: https://docs.djangoproject.com/en/1.9/ref/settings/

# DATABASES
Wiggum was implemented with Postgresql in mind and is the only database tested, but
Django allows more databases, you choose what to use but have in mind that Postgres
is the recommended one.

Set the databases settings with this schema

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'XXXXXXX',
        'PASSWORD': 'XXXXXXXXX',
        'HOST': "XXXXXXXXXXX",
        'PORT': 5432,
    },
}
```

# ALLOWED_HOSTS
In this setting ou will need to set the hosts where your wiggum instances will be
listening, private and public ones. For example:

```python
ALLOWED_HOSTS = [
    'login.wiggum.io',
    'login.priv.wiggum.io',
    '127.0.0.1',
]
```

# DEBUG
Set wiggum app in debug mode

```python
DEBUG = True
```

!!! note
    Deactivated by default

# SECRET_KEY
The Django secret key for singing sessions

```python
SECRET_KEY = '8hcmch1@o&a5bjsx_56x5e4(gmc-6!g48x**usqelv_r9ok_-!'
```

!!! warning
    This setting should be private!
