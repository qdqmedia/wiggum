from django.conf import settings
from django.conf.urls import include, url
from django.views.generic import TemplateView

from . import apiv1
from administrator import admin
from authorization import urls as auth_urls


api_url = "^api/{version}/".format(version=settings.API_VERSION)

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^a/', include(auth_urls, namespace='auth')),
    url(api_url, include(apiv1.urlpatterns, namespace='api')),
    url(r'^easter-egg/', TemplateView.as_view(template_name='easter-egg.html'), name='easter-egg'),
    url(r'^unauthorized/', TemplateView.as_view(template_name='unauthorized.html'), name='unauthorized'),
    url(r'^admin/', include(admin.urls)),

    # Swagger docs for the api
    url(r'^docs/', include('rest_framework_swagger.urls')),

    # Prometheus urls
    url('', include('django_prometheus.urls')),

    # Robots.txt
    url(r'^robots.txt$', TemplateView.as_view(
        template_name="robots.txt",
        content_type="text/plain"), name='unauthorized'),
]

# 404 and 505 templates
handler404 = 'wiggum.views.handler404'
handler505 = 'wiggum.views.handler505'
