from django.contrib import admin

from administrator import admin as wiggum_admin
from .models import User, ProjectPermission
from .forms import CustomUserCreationForm, CustomUserEditForm


@admin.register(User, site=wiggum_admin)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'active', 'external_service')
    list_filter = ('project_permissions',)
    search_fields = ('username', 'email', 'first_name', 'last_name', 'external_service')

    #fieldsets = (
    #    (None, {
    #        'fields': ('username', 'email', 'first_name', 'last_name',
    #                   'password1', 'password2', 'project_permissions')
    #    }),
    #)

    def get_form(self, request, obj=None, **kwargs):
        # On creation show CustomUserCreationForm
        if obj is None:
            return CustomUserCreationForm
        else:  # On edition show CustomUserCreationForm
            return CustomUserEditForm


@admin.register(ProjectPermission, site=wiggum_admin)
class ProjectPermissionAdmin(admin.ModelAdmin):
    list_display = ('key', 'active',)
    search_fields = ('key',)
