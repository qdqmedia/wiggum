from django.contrib import admin

from administrator import admin as wiggum_admin
from .models import Application
from .forms import ApplicationCreationForm, ApplicationEditForm
from .utils import generate_api_key


# Admin action to reset tokens
def reset_application_token(modeladmin, request, queryset):
    for i in queryset:
        i.token = generate_api_key()
        i.save()
reset_application_token.short_description = "Reset selected applications tokens"


def deactivate_application_token(modeladmin, request, queryset):
    queryset.update(active=False)
deactivate_application_token.short_description = "Deactivate selected applications"


def activate_application_token(modeladmin, request, queryset):
    queryset.update(active=True)
activate_application_token.short_description = "Activate selected applications"


@admin.register(Application, site=wiggum_admin)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'token', 'active')
    search_fields = ('token', 'description')
    actions = [reset_application_token, deactivate_application_token,
               activate_application_token]

    def get_form(self, request, obj=None, **kwargs):
        # On creation dont show the token
        if obj is None:
            self.readonly_fields = ()
            return ApplicationCreationForm

        # In edit mode we need the read only to be visible
        if not self.readonly_fields:
            self.readonly_fields = ('token', )
        return ApplicationEditForm
