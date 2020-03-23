from django.urls import path

from settings.views import SettingsView, ProfileViewSet, PasswordViewSet, \
    AvatarViewSet, TwoFactorViewSet

urlpatterns = [
    path('', SettingsView.as_view(), name='settings'),
    path('basic/',
         ProfileViewSet.as_view({'patch': 'patch'}),
         name='profile'),
    path('change-password/',
         PasswordViewSet.as_view({'post': 'update'}),
         name='change-password'),
    path('change-avatar/',
         AvatarViewSet.as_view({'post': 'post', 'delete': 'delete'}),
         name='change-avatar'),
    path('two-factor/',
         TwoFactorViewSet.as_view({'get': 'get'}),
         name='two-factor'),
    path('two-factor/<slug:uidb64>/<slug:utokenb64>/',
         TwoFactorViewSet.as_view({'post': 'post'}),
         name='two-factor-toggle')
]
