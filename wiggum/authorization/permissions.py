import re

from rest_framework.permissions import BasePermission

from applications.models import Application


auth_regex = re.compile("Bearer +([a-fA-F0-9]{32})")


class AppIsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        auth_header = request.META.get('HTTP_AUTHORIZATION', "")
        token_regex_group = auth_regex.match(auth_header)
        # Don't hit the database if no token
        if token_regex_group:
            token = token_regex_group.group(1)
            try:
                # Correct token?
                app = Application.objects.get(token=token)
                # is app active?
                if app.active:
                    return True
                # TODO: Check permissions
            except Application.DoesNotExist:
                pass
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
