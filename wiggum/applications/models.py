import os

from django.core import validators
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from users.models import ProjectPermission
from .utils import generate_api_key


DEFAULT_THEME = settings.WIGGUM_DEFAULT_THEME
THEMES = [(i, i) for i in os.listdir(
    os.path.join(settings.BASE_DIR, "..", 'themes/templates'))]


class Application(models.Model):
    """App representation"""

    name = models.CharField(_('Application name'),
                            max_length=100,
                            blank=False,
                            null=False,
                            unique=True)
    token = models.CharField(_('Application token'),
                             max_length=32,
                             default=generate_api_key,
                             blank=False,
                             null=False,
                             validators=[validators.RegexValidator(
                                r'^[a-fA-F0-9]{32}$',
                                _('Key should be hexadecimal and length 32')
                                ), ],
                             unique=True)
    description = models.TextField(_('Application description'),
                                   blank=True,
                                   null=False)
    active = models.BooleanField(_('Application active'), default=True)
    project_permissions = models.ManyToManyField(ProjectPermission,
                                                 blank=True)
    theme = models.CharField(_('App associated theme'),
                             choices=THEMES,
                             default=DEFAULT_THEME,
                             max_length=50,)

    def __str__(self):
        return "{0}({1})".format(self.name, self.token)
