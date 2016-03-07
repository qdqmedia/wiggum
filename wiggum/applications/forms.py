from django import forms

from .models import Application


class ApplicationCreationForm(forms.ModelForm):

    class Meta:
        model = Application
        exclude = ('token', )


class ApplicationEditForm(forms.ModelForm):

    class Meta:
        model = Application
        fields = ('name', 'description', 'project_permissions', 'active',
                  'theme')