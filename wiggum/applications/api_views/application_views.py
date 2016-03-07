import logging

from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from ..models import Application
from ..serializers import ApplicationSerializer
from ..utils import generate_api_key

logger = logging.getLogger(__name__)


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows application to be viewed or edited.
    """
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    @detail_route(methods=['get'],  url_path='reset-token')
    def reset_token(self, request, pk=None):

        try:
            app = self.get_object()
            app.token = generate_api_key()
            app.save()
            logging.debug("New token for app {0}: {1}".format(app, app.token))
            return Response({
                'status': 'token set',
                'token': app.token,
            })
        except Exception as e:
            logging.error("Error resetting token: {0}".format(e),
                          extra={'request': request})
            return Response("Error reseting token",
                            status=status.HTTP_400_BAD_REQUEST)
