from rest_framework import serializers

from users.models import ProjectPermission
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):

    project_permissions = serializers.SlugRelatedField(
        many=True,
        slug_field="key",
        required=False,
        queryset=ProjectPermission.objects
    )

    class Meta:
        model = Application
        read_only_fields = ('token', )
