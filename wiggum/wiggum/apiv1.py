from django.conf.urls import patterns, url, include
from rest_framework import routers

from users.api_views import (user_views, project_permission_views,
                             username_views)
from applications.api_views import application_views


router = routers.DefaultRouter()

# User urls
router.register(r'users', user_views.UserViewSet)
router.register(r'usernames',
                username_views.UsernameViewSet,
                base_name="username")
router.register(r'project-permissions',
                project_permission_views.ProjectPermissionViewSet)
router.register(r'applications', application_views.ApplicationViewSet)


urlpatterns = patterns('',
    url(r'^', include(router.urls)),
)
