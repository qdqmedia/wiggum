import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password=None, isAdmin=False,
                      **extra_fields):
        if not username:
            raise ValueError('The given username must be set')

        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)  # Many to many needs to save before linking

        if isAdmin:
            # Set admin for the app
            p = ProjectPermission.objects.get(
                key=settings.APP_PERMISSION_KEYS['admin'])
            user.project_permissions.add(p)

        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password=None, **extra_fields):
        return self._create_user(username, email, password, True,
                                  **extra_fields)


class ProjectPermission(models.Model):
    """Permissions for the user accesses """

    key = models.CharField(_('Project permission key'),
                           max_length=200,
                           blank=False,
                           null=False,
                           unique=True)
    description = models.TextField(_('Project permission description'),
                                   blank=True,
                                   null=False)
    active = models.BooleanField(_('Project permission active'), default=True)

    def __str__(self):
        return self.key


class User(AbstractBaseUser):
    """ Our custom user using the django standard abstract base user with extra
        fields
    """
    project_permissions = models.ManyToManyField(ProjectPermission, blank=True)
    username = models.CharField(
        _('Username'),
        max_length=39,
        unique=True,
        help_text=_('Required. 39 characters or fewer.  alphanumeric characters or single hyphens, and cannot begin or end with a hyphen'),
        validators=[
            validators.RegexValidator(
                r'^[a-zA-Z0-9][a-zA-Z0-9A-Z\-]*[a-zA-Z0-9]+$',
                _('Username may only contain alphanumeric characters or single hyphens, and cannot begin or end with a hyphen')
            ),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _('Email address'),
        unique=True,
        max_length=200,
        error_messages={
            'unique': _("A user with that email already exists."),
        },)
    first_name = models.CharField(_('First name'), max_length=50, blank=True)
    last_name = models.CharField(_('Last name'), max_length=50, blank=True)
    date_joined = models.DateTimeField(_('Date joined'), default=timezone.now)
    active = models.BooleanField(_('Active'), default=True)
    password_reset_token = models.UUIDField(
        _('Password reset token'),
        default=uuid.uuid4,
        editable=False,
        unique=True)
    password_reset_token_expire = models.DateTimeField(_('Password reset token expiration'), default=timezone.now)
    sfa_token_expire = models.DateTimeField(_('SFA token expiration'), default=timezone.now)
    sfa_token = models.UUIDField(
        _('SFA token'),
        default=uuid.uuid4,
        editable=False,
        unique=True)
    external_service = models.CharField(_('External service'), max_length=50, blank=True)

    # backwards relation (related name) will be "users"

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def get_full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.username

    # Django admin needs these methods/properties
    def is_admin(self):
        """ This property bypasses the admin login """
        if self.project_permissions.filter(
                key=settings.APP_PERMISSION_KEYS['admin']).exists():
            return True
        return False

    @property
    def is_staff(self):
        return self.is_admin()

    @property
    def is_superuser(self):
        return self.is_admin()

    def has_perm(self, perm, obj=None):
        return self.is_admin()

    def has_module_perms(self, app_label):
        return self.is_admin()

    def __str__(self):
        return "{username}({email})".format(
            username=self.username,
            email=self.email)
