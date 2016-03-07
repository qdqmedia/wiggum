from django.contrib.admin import AdminSite

from authorization.views import LoginView, LogoutView


class WiggumAdmin(AdminSite):
    site_header = 'Wiggum admin'

admin = WiggumAdmin(name='wiggum')

# Customize our administrator
admin.login = LoginView.as_view()
admin.logout = LogoutView.as_view()
