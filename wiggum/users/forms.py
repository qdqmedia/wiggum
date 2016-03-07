from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from .models import User, ProjectPermission


class CustomUserCreationForm(UserCreationForm):
    """ Custom freation form for a user creation"""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1',
                  'password2', 'project_permissions', 'external_service',
                  'active')

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'duplicate_email': _("Email already exists"),
        'duplicate_username': _("Username already exists"),
    }
    project_permissions = forms.ModelMultipleChoiceField(
        queryset=ProjectPermission.objects.all(), required=False)
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                self.error_messages['duplicate_username'],
                code='duplicate_username')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                self.error_messages['duplicate_email'],
                code='duplicate_email')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password1"]
        user.set_password(password)

        if commit:
            user.save()
        return user


class CustomUserEditForm(forms.ModelForm):
    """ Same form as CustomUserCreationForm except this one doesn't need a
        password to edit
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1',
                  'password2', 'project_permissions', 'last_login', 'date_joined',
                  'external_service', 'active')
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."), }

    password1 = forms.CharField(required=False,
                                label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(required=False,
                                label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        if password1:
            password2 = self.cleaned_data.get("password2")
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
            return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password1"]
        if password:
            user.set_password(password)

        if commit:
            user.save()
        return user
