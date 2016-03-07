
from .user_views import UserViewSet


class UsernameViewSet(UserViewSet):
    """Handy endpoint to use the api by username instead of id/pk"""

    lookup_field = "username"
    lookup_url_kwarg = "pk" # Used this kwarg to be compatible with custom detail views
