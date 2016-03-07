from django.conf import settings
from django.test import TransactionTestCase
from django.db.utils import IntegrityError
from .models import User, ProjectPermission


class UserModelTest(TransactionTestCase):

    def setUp(self):
        # Add admin permission for the test (this is on migrations but django
        # flushes the data)
        try:
            ProjectPermission(key=settings.APP_PERMISSION_KEYS['admin']).save()
        except IntegrityError:
            pass  # first run will have the data already from the migrations

        # Initial data
        self.data = [{
            'email': "brucewayne@batman.com",
            'username': "dark-knight4",
            'first_name': "Bruce",
            'last_name': "Wayne", }, {

            'email': "peterparker@spiderman.com",
            'username': "spidy12",
            'first_name': "Peter",
            'last_name': "Parker", },
        ]
        self.password = "test"

    def test_creation(self):
        for i in self.data:
            u = User(username=i['username'],
                     email=i['email'],
                     first_name=i['first_name'],
                     last_name=i['last_name'],)
            u.save()
            u2 = User.objects.get(email=i['email'])

            for k, _ in i.items():
                self.assertEqual(getattr(u2, k), getattr(u, k))

    def test_unique_fields(self):
        for i in self.data:
            User(username=i['username'],
                 email=i['email'],
                 first_name=i['first_name'],
                 last_name=i['last_name'],).save()
            # Check username unique constraint
            with self.assertRaises(IntegrityError):
                User(username=i['username'],
                     email="brucewayne1@batman.com",
                     first_name=i['first_name'],
                     last_name=i['last_name'],).save()
            # Check email unique constraint
            with self.assertRaises(IntegrityError):
                User(username="dark-knight5",
                     email=i['email'],
                     first_name=i['first_name'],
                     last_name=i['last_name'],).save()

    def test_create_user(self):
        for i in self.data:
            User.objects.create_user(username=i['username'],
                                     email=i['email'],
                                     password=self.password)
            u = User.objects.get(email=i['email'])
            self.assertTrue(u.check_password(self.password))

    def test_create_superuser(self):
        for i in self.data:
            User.objects.create_superuser(username=i['username'],
                                          email=i['email'],
                                          password=self.password)
            u = User.objects.get(email=i['email'])
            self.assertTrue(u.check_password(self.password))

            # Check is admin
            self.assertTrue(u.is_admin())
            self.assertTrue(u.is_staff)
            self.assertTrue(u.is_superuser)
            self.assertTrue(u.has_perm(None))
            self.assertTrue(u.has_module_perms(None))


class ProjectPermissionModelTest(TransactionTestCase):

    def setUp(self):
        self.data = [{
            'key': "someapp.something.write",
            'description': "Some app write permissions on something", },{
            'key': "someapp.something.read",
            'description': "Some app read permissions on something", }, {
            'key': "someapp.all",
            'description': "Some app admin permissions", }
        ]

    def test_creation(self):
        for i in self.data:
            p = ProjectPermission(key=i['key'],
                                  description=i['description'])
            p.save()

            p2 = ProjectPermission.objects.get(key=i['key'])
            for k, _ in i.items():
                self.assertEqual(getattr(p2, k), getattr(p, k))

    def test_unique_fields(self):
        for i in self.data:
            ProjectPermission(key=i['key'],
                              description=i['description']).save()
            # Check key unique constraint
            with self.assertRaises(IntegrityError):
                ProjectPermission(key=i['key'],
                                  description=i['description']).save()

    def test_user_backwards(self):
        p = ProjectPermission(key=settings.APP_PERMISSION_KEYS['admin'])
        p.save()

        u = User(username="test",
                 email="test@test.com",
                 first_name="test",
                 last_name="test")
        u.save()
        u.project_permissions.add(p)
        u.save()

        p.refresh_from_db()
        u.refresh_from_db()

        self.assertTrue(len(p.user_set.all()) == 1)
        self.assertTrue(len(u.project_permissions.all()) == 1)
