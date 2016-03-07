from rest_framework import viewsets

from ..models import ProjectPermission
from ..serializers import ProjectPermissionSerializer


class ProjectPermissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user to be viewed or edited.
    """
    queryset = ProjectPermission.objects.all()
    serializer_class = ProjectPermissionSerializer
