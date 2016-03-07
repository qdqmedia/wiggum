from django.conf import settings
from django.test import TransactionTestCase
from django.db.utils import IntegrityError
from .models import Application
from users.models import ProjectPermission
from .utils import generate_api_key


class ApplicationModelTest(TransactionTestCase):
    def setUp(self):
        # Initial data
        self.data = [{
            'name': "Batman application",
            'token': generate_api_key(),
            'description': "Bruce Wayne awesome application",
            'active': True, }, {

            'name': "Spiderman application",
            'token': generate_api_key(),
            'description': "Peter parker awesome application",
            'active': False, },
        ]

    def test_creation(self):
        for i in self.data:
            a = Application(name=i['name'],
                            token=i['token'],
                            description=i['description'],
                            active=i['active'],)
            a.save()
            a2 = Application.objects.get(token=i['token'])

            for k, _ in i.items():
                self.assertEqual(getattr(a2, k), getattr(a, k))

    def test_unique_fields(self):
        for i in self.data:
            Application(name=i['name'], token=i['token']).save()

            with self.assertRaises(IntegrityError):
                Application(name=i['name'], token=generate_api_key()).save()

            with self.assertRaises(IntegrityError):
                Application(name="test", token=i['token']).save()

    def test_Application_backwards(self):
        p = ProjectPermission(key="test")
        p.save()

        a = Application(name="test", token=generate_api_key())
        a.save()
        a.project_permissions.add(p)
        a.save()

        a2 = Application(name="test2", token=generate_api_key())
        a2.save()
        a2.project_permissions.add(p)
        a2.save()

        p.refresh_from_db()
        a.refresh_from_db()
        a2.refresh_from_db()

        self.assertTrue(len(p.application_set.all()) == 2)
        self.assertTrue(len(a.project_permissions.all()) == 1)
        self.assertTrue(len(a2.project_permissions.all()) == 1)
