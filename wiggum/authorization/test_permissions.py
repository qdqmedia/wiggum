from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from applications.models import Application


class AuthorizedApiTestCase(APITestCase):
    """Testcase with api authentication prepared on the client"""
    def setUp(self):
        # Create an api token so we could test
        a = Application(name="Test wiggum")
        a.save()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {0}'.format(a.token))


class PermissionsApiTest(APITestCase):
    def test_ap_is_authenticated(self):
        url = reverse('api:user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Create an api token so we could test
        a = Application(name="Test permissions")
        a.save()
        authorized_client = APIClient()
        authorized_client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(a.token))

        response = authorized_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
