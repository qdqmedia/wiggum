from django.core.urlresolvers import reverse
from rest_framework import status

from authorization.test_permissions import AuthorizedApiTestCase
from applications.models import Application
from .models import ProjectPermission


class ApplicationApiTest(AuthorizedApiTestCase):
    def setUp(self):
        super().setUp()

        # Initial api auth application:
        self.initial_application_number = 1
        # Create neccessary data
        self.applications_data = [{
            'name': "Batman application",
            'description': "Bruce Wayne awesome application",
            'active': True, }, {

            'name': "Spiderman application",
            'description': "Peter parker awesome application",
            'active': False, },
        ]

        self.applications = []
        for i in self.applications_data:
            a = Application(name=i['name'],
                            description=i['description'],
                            active=i['active'])
            a.save()
            self.applications.append(a)

    def test_list(self):
        url = reverse('api:application-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.applications_data) +
                         self.initial_application_number)

    def test_create(self):
        test_application = {
            'name': "Test application",
            'description': "Awesome test applications",
        }

        url = reverse('api:application-list')
        response = self.client.post(url, test_application)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        u = Application.objects.get(id=response.data['id'])
        for k, v in test_application.items():
                self.assertEqual(v, getattr(u, k))

    def test_detail(self):
        for i in self.applications:
            url = reverse('api:application-detail', args=[i.id])
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(i.name, response.data['name'])
            self.assertEqual(i.description, response.data['description'])
            self.assertEqual(i.token, response.data['token'])
            self.assertEqual(i.active, response.data['active'])

    def test_update(self):
        prefix = "updated"
        for i in self.applications_data:
            a = Application.objects.get(name=i['name'])
            url = reverse('api:application-detail', args=[a.id])
            i['name'] = "{0}{1}".format(prefix, i['name'])
            i['description'] = "{0}{1}".format(prefix, i['description'])
            response = self.client.put(url, i)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            a.refresh_from_db()
            self.assertEqual(a.name, i['name'])
            self.assertEqual(a.description, i['description'])

    def test_delete(self):
        for i in self.applications:
            url = reverse('api:application-detail', args=[i.id])
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        url = reverse('api:application-list')
        response = self.client.get(url)
        self.assertEqual(self.initial_application_number, len(response.data))

    def test_application_permissions_relation(self):
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
        for i in self.applications_data:
            a = Application.objects.get(name=i['name'])
            url = reverse('api:application-detail', args=[a.id])
            # Set the keys
            i['project_permissions'] = [x['key'] for x in permission_data]
            response = self.client.put(url, i)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            a.refresh_from_db()

            # Check
            self.assertEqual(len(permission_data),
                             len(a.project_permissions.all()))

    def test_application_reset_token(self):
        for i in self.applications:
            url = reverse('api:application-reset-token', args=[i.id])
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            prev_token = i.token
            i.refresh_from_db()
            self.assertNotEqual(response.data['token'], prev_token)
            self.assertEqual(response.data['token'], i.token)
