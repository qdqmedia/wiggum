from django.contrib.auth.hashers import make_password

from rest_framework import serializers

from .models import User, ProjectPermission
from applications.models import Application


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'},
                                     write_only=True,
                                     required=False)

    project_permissions = serializers.SlugRelatedField(
        many=True,
        slug_field="key",
        required=False,
        queryset=ProjectPermission.objects
    )

    class Meta:
        model = User
        read_only_fields = ('last_login', 'date_joined')
        exclude = ('password_reset_token', 'password_reset_token_expire',
                   'sfa_token', 'sfa_token_expire')

    def create(self, validated_data):
        # Set the password correctly
        if validated_data.get('password', None):
            raw_password = validated_data['password']
            validated_data['password'] = make_password(raw_password)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('password', None):
            raw_password = validated_data['password']
            validated_data['password'] = make_password(raw_password)

        instance.password = validated_data.get('password', instance.password)
        return super().update(instance, validated_data)


class ProjectPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPermission

    user_set = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        queryset=User.objects
    )

    application_set = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        queryset=Application.objects
    )
