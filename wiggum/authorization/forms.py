from django import forms
from django.utils.translation import ugettext_lazy as _


def get_redirect_uri(cleaned_data):
    uri = cleaned_data['redirect_uri']
    if uri and uri != str(None):
        return cleaned_data['redirect_uri']


class LoginForm(forms.Form):
    username_or_email = forms.CharField(label=_("Username or email"),
                                        required=True)
    password = forms.CharField(label=_("Password"),
                               required=True, widget=forms.PasswordInput)
    redirect_uri = forms.CharField(label=_("Redirection uri"),
                                   required=False, widget=forms.HiddenInput())

    def get_redirect_uri(self):
        return get_redirect_uri(self.cleaned_data)


class RecoverPasswordForm(forms.Form):
    email = forms.EmailField(label=_("Email"), required=True)
    redirect_uri = forms.CharField(label=_("Redirection uri"),
                                   required=False, widget=forms.HiddenInput())

    def get_redirect_uri(self):
        return get_redirect_uri(self.cleaned_data)

    error_messages = {
        'not_valid_email': _("The email is not valid"),
    }

# Don't check, this will be checked by the actions (check RECOVER_PASS_REQUEST_ACTIONS)
#    def clean_email(self):
#        email = self.cleaned_data.get("email")
#
#        if not User.objects.filter(email=email).exists():
#            raise forms.ValidationError(
#                self.error_messages['not_valid_email'],
#                code='not_valid_email',
#            )
#
#        return email


class ResetPasswordForm(forms.Form):
    password = forms.CharField(label=_("Password"), required=True,
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password validation"), required=True,
                                widget=forms.PasswordInput)

    redirect_uri = forms.CharField(label=_("Redirection uri"),
                                   required=False, widget=forms.HiddenInput())

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    def get_redirect_uri(self):
        return get_redirect_uri(self.cleaned_data)


    def clean_password2(self):
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2
