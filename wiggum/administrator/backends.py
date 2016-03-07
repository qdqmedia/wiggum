from django.conf import settings

from authorization.backends import JWTAuthentication
from authorization import jwt_utils
from users.models import User


# In order to don't mess up the authentication backends we inherit from that
# backend and implement django's auth backends neccessary methods
class JWTAuthBackend(JWTAuthentication):
    def authenticate(self, request, *args, **kwargs):
        return super().authenticate(request)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def clean_id(self, request):
        jwt = request.COOKIES.get(settings.JWT_COOKIE_NAME, None)
        if jwt and jwt_utils.validate_jwt_all_keys(jwt):
            try:
                jwt_decoded = jwt_utils.decode_jwt(jwt)
                return jwt_decoded['user']['id']
            except KeyError:
                pass
