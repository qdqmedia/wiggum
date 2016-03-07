import datetime
import time

from django.core.urlresolvers import reverse
from django.utils import timezone
from rest_framework import status

from .models import User, ProjectPermission
from applications.models import Application
from authorization.test_permissions import AuthorizedApiTestCase


class UserApiTest(AuthorizedApiTestCase):

    API_PREFIX = "user"

    API_URLS = {
        "list": "api:{0}-list",
        "detail": "api:{0}-detail",
        "reset-password-url": "api:{0}-reset-password-url",
        "sfa-url": "api:{0}-sfa-url",
    }

    def setUp(self):
        super().setUp()
        # Create neccessary data
        self.users_data = [{
            'email': "brucewayne@batman.com",
            'username': "dark-knight4",
            'first_name': "Bruce",
            'last_name': "Wayne", }, {

            'email': "peterparker@spiderman.com",
            'username': "spidy12",
            'first_name': "Peter",
            'last_name': "Parker", },
        ]
        self.users = []
        for i in self.users_data:
            u = User(username=i['username'],
                     email=i['email'],
                     first_name=i['first_name'],
                     last_name=i['last_name'],)
            u.save()
            self.users.append(u)

    def get_user_id(self, user):
        """ Gets the correct id for the api rest endpoint"""
        return user.id

    def get_api_urls(self, url_key):
        return self.__class__.API_URLS[url_key].format(
            self.__class__.API_PREFIX)

    def test_list(self):
        url = reverse(self.get_api_urls("list"))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.users_data))

    def test_create(self):
        test_user = {
            'email': "test@api.com",
            'username': "testapi87",
            'first_name': "test",
            'last_name': "api",
            'password': "apitest",
        }

        url = reverse(self.get_api_urls("list"))
        response = self.client.post(url, test_user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        u = User.objects.get(id=response.data['id'])
        for k, v in test_user.items():
            if k != 'password':
                self.assertEqual(v, getattr(u, k))
            else:
                self.assertTrue(u.check_password(v))

    def test_detail(self):
        for i in self.users:
            url = reverse(self.get_api_urls("detail"),
                          args=[self.get_user_id(i)])

            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(i.username, response.data['username'])
            self.assertEqual(i.email, response.data['email'])
            self.assertEqual(i.active, response.data['active'])
            self.assertEqual(i.first_name, response.data['first_name'])
            self.assertEqual(i.last_name, response.data['last_name'])

    def test_update(self):
        prefix = "updated"
        for i in self.users_data:
            u = User.objects.get(email=i['email'])
            url = reverse(self.get_api_urls("detail"),
                          args=[self.get_user_id(u)])
            i['username'] = "{0}{1}".format(prefix, i['username'])
            i['email'] = "{0}{1}".format(prefix, i['email'])
            response = self.client.put(url, i)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            u.refresh_from_db()
            self.assertEqual(u.username, i['username'])
            self.assertEqual(u.email, i['email'])
            self.assertEqual(u.first_name, i['first_name'])
            self.assertEqual(u.last_name, i['last_name'])

    def test_delete(self):
        for i in self.users:
            url = reverse(self.get_api_urls("detail"),
                          args=[self.get_user_id(i)])
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        url = reverse(self.get_api_urls("list"),)
        response = self.client.get(url)
        self.assertEqual(0, len(response.data))

    def test_user_permissions_relation(self):
        permission_data = [{
            'key': "someapp.something.write",
            'description': "Some app write permissions on something", }, {
            'key': "someapp.something.read",
            'description': "Some app read permissions on something", }, {
            'key': "someapp.all",
            'description': "Some app admin permissions", }
        ]
        for i in permission_data:
            p = ProjectPermission(key=i['key'],
                                  description=i['description'])
            p.save()

        # Update objects with permissions
        for i in self.users_data:
            u = User.objects.get(email=i['email'])
            url = reverse(self.get_api_urls("detail"),
                          args=[self.get_user_id(u)])
            # Set the keys
            i['project_permissions'] = [x['key'] for x in permission_data]
            response = self.client.put(url, i)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            u.refresh_from_db()

            # Check
            self.assertEqual(len(permission_data),
                             len(u.project_permissions.all()))

    def test_password_update(self):
        for i in self.users_data:
            u = User.objects.get(email=i['email'])
            url = reverse(self.get_api_urls("detail"),
                          args=[self.get_user_id(u)])
            i['password'] = i['username']
            response = self.client.put(url, i)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            u.refresh_from_db()
            self.assertTrue(u.check_password(i['username']))

    def test_password_reset_token(self):
        for i in self.users_data:
            u = User.objects.get(email=i['email'])
            url = reverse(self.get_api_urls("reset-password-url"),
                          args=[self.get_user_id(u)])
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertNotEqual(u.password_reset_token, response.data['token'])

            u.refresh_from_db()
            self.assertEqual(u.password_reset_token, response.data['token'])

    def test_password_reset_token_with_expiration_seconds(self):
        for i in self.users_data:
            u = User.objects.get(email=i['email'])
            url = reverse(self.get_api_urls("reset-password-url"),
                          args=[self.get_user_id(u)])
            url = "{0}?expiration_seconds=1".format(url)
            response = self.client.get(url)
            time.sleep(1)
            now = timezone.now()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertNotEqual(u.password_reset_token, response.data['token'])

            u.refresh_from_db()
            self.assertEqual(u.password_reset_token, response.data['token'])

            # Check expiration
            self.assertTrue(now > response.data['expire'])

    def test_sfa_token(self):
        for i in self.users_data:
            u = User.objects.get(email=i['email'])
            url = reverse(self.get_api_urls("sfa-url"),
                          args=[self.get_user_id(u)])
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertNotEqual(u.sfa_token, response.data['token'])

            u.refresh_from_db()
            self.assertEqual(u.sfa_token, response.data['token'])

    def test_sfa_token_with_expiration_seconds(self):
        for i in self.users_data:
            u = User.objects.get(email=i['email'])
            url = reverse(self.get_api_urls("sfa-url"),
                          args=[self.get_user_id(u)])
            url = "{0}?expiration_seconds=1".format(url)
            response = self.client.get(url)
            time.sleep(1)
            now = timezone.now()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertNotEqual(u.sfa_token, response.data['token'])

            u.refresh_from_db()
            self.assertEqual(u.sfa_token, response.data['token'])

            # Check expiration
            self.assertTrue(now > response.data['expire'])


class UsernameApiTest(UserApiTest):
    """The same as UserApiTest but with id as username instead of pk"""

    API_PREFIX = "username"

    def get_user_id(self, user):
        """ Gets the correct id for the api rest endpoint"""
        return user.username


class PermissionApiTest(AuthorizedApiTestCase):
    def setUp(self):
        super().setUp()

        # Migration permissions
        self.migration_permissions_number = len(ProjectPermission.objects.all())

        # Create neccessary data
        self.permissions_data = [{
            'key': "someapp.something.write",
            'description': "Some app write permissions on something", }, {
            'key': "someapp.something.read",
            'description': "Some app read permissions on something", }, {
            'key': "someapp.all",
            'description': "Some app admin permissions", }
        ]
        self.permissions = []
        for i in self.permissions_data:
            p = ProjectPermission(key=i['key'],
                                  description=i['description'])
            p.save()
            self.permissions.append(p)

    def test_list(self):
        url = reverse('api:projectpermission-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data),
            len(self.permissions_data) + self.migration_permissions_number)

    def test_create(self):
        test_permission = {
            'key': "test.permission.write",
            'description': "Test permission",
        }

        url = reverse('api:projectpermission-list')
        response = self.client.post(url, test_permission)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        u = ProjectPermission.objects.get(id=response.data['id'])
        for k, v in test_permission.items():
                self.assertEqual(v, getattr(u, k))

    def test_detail(self):
        for i in self.permissions:
            url = reverse('api:projectpermission-detail', args=[i.id])
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(i.key, response.data['key'])
            self.assertEqual(i.description, response.data['description'])

    def test_update(self):
        prefix = "updated"
        for i in self.permissions_data:
            p = ProjectPermission.objects.get(key=i['key'])
            url = reverse('api:projectpermission-detail', args=[p.id])
            i['key'] = "{0}{1}".format(prefix, i['key'])
            i['description'] = "{0}{1}".format(prefix, i['description'])
            response = self.client.put(url, i)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            p.refresh_from_db()
            self.assertEqual(p.key, i['key'])
            self.assertEqual(p.description, i['description'])

    def test_delete(self):
        for i in self.permissions:
            url = reverse('api:projectpermission-detail', args=[i.id])
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        url = reverse('api:projectpermission-list')
        response = self.client.get(url)
        self.assertEqual(self.migration_permissions_number, len(response.data))

    def test_user_permissions_relation(self):
        users_data = [{
            'email': "brucewayne@batman.com",
            'username': "dark-knight4",
            'first_name': "Bruce",
            'last_name': "Wayne", }, {

            'email': "peterparker@spiderman.com",
            'username': "spidy12",
            'first_name': "Peter",
            'last_name': "Parker", },
        ]
        users = []
        for i in users_data:
            u = User(username=i['username'],
                     email=i['email'],
                     first_name=i['first_name'],
                     last_name=i['last_name'],)
            u.save()
            users.append(u)

        # Update objects with permissions
        for i in self.permissions_data:
            p = ProjectPermission.objects.get(key=i['key'])
            url = reverse('api:projectpermission-detail', args=[p.id])
            # Set the keys
            i['user_set'] = [x.id for x in users]
            response = self.client.put(url, i)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            p.refresh_from_db()

            # Check
            self.assertEqual(len(users_data), len(p.user_set.all()))

    def test_application_permissions_relation(self):
        applications_data = [{
            'name': "Batman application",
            'description': "Bruce Wayne awesome application",
            'active': True, }, {

            'name': "Spiderman application",
            'description': "Peter parker awesome application",
            'active': False, },
        ]

        applications = []
        for i in applications_data:
            a = Application(name=i['name'],
                            description=i['description'],
                            active=i['active'])
            a.save()
            applications.append(a)

        for i in self.permissions_data:
            p = ProjectPermission.objects.get(key=i['key'])
            url = reverse('api:projectpermission-detail', args=[p.id])
            # Set the keys
            i['application_set'] = [x.id for x in applications]
            response = self.client.put(url, i)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            p.refresh_from_db()

            # Check
            self.assertEqual(len(applications_data),
                             len(p.application_set.all()))
