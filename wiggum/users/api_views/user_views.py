import logging

from django.core.urlresolvers import reverse

from rest_framework import viewsets
from rest_framework import filters
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from ..models import User
from ..serializers import UserSerializer
from ..utils import (refresh_sfa_token, create_password_reset_url)

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('username', 'id', 'email')

    @detail_route(methods=['get'],  url_path='reset-password-url')
    def reset_password_url(self, request, pk=None):
        user = self.get_object()

        expiration_delta_sec = request.query_params.get("expiration_seconds")
        if expiration_delta_sec:
            expiration_delta_sec = int(expiration_delta_sec)

        url = create_password_reset_url(user, expiration_delta_sec)

        logger.debug("[API] Password recover url created: {0}".format(url))
        return Response({
            'status': 'password reset url created',
            'token': user.password_reset_token,
            'expire': user.password_reset_token_expire,
            'url': request.build_absolute_uri(url),
            'email': user.email,
            'id': user.id,
        })

    @detail_route(methods=['get'],  url_path='sfa-url')
    def sfa_url(self, request, pk=None):
        user = self.get_object()

        expiration_delta_sec = request.query_params.get("expiration_seconds")
        if expiration_delta_sec:
            expiration_delta_sec = int(expiration_delta_sec)
        refresh_sfa_token(user, expiration_delta_sec)

        # Get url
        url = reverse('auth:sfa', kwargs={
            'user_id': user.id,
            'uuid': str(user.sfa_token)
        })

        logger.debug("[API] sfa url created: {0}".format(url))
        return Response({
            'status': 'sfa url created',
            'token': user.sfa_token,
            'expire': user.sfa_token_expire,
            'url': request.build_absolute_uri(url),
            'email': user.email,
            'id': user.id,
        })
