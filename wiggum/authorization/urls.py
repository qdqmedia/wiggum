from django.conf.urls import patterns, url

from .views import (LoginView, JWTTesView, ResetPasswordView,
                    RecoverPasswordView, CloneCookieView, LogoutView,
                    ImpersonateView, SFAView)

urlpatterns = patterns('',
    url(r'^login/$',
        LoginView.as_view(),
        name='login'),

    url(r'^reset-password/(?P<user_id>[0-9]+)/(?P<uuid>[0-9a-zA-Z\-]{36})$',
        ResetPasswordView.as_view(),
        name='reset-password'),

    url(r'^recover-password$',
        RecoverPasswordView.as_view(),
        name='recover-password'),

    url(r'^test/jwt$',
        JWTTesView.as_view(),
        name='test-jwt'),

    url(r'^clone/(?P<token>[a-zA-Z0-9\-\_\.]+)$',
        CloneCookieView.as_view(),
        name='clone-cookie'),

    url(r'^logout/$',
        LogoutView.as_view(),
        name='logout'),

    url(r'^impersonate/(?P<user_id>[0-9]+)$',
        ImpersonateView.as_view(),
        name='impersonate'),

    url(r'^sfa/(?P<user_id>[0-9]+)/(?P<uuid>[0-9a-zA-Z\-]{36})$',
        SFAView.as_view(),
        name='sfa'),
)
