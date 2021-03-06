from django.contrib.auth.views import PasswordResetView, \
    PasswordChangeView, PasswordResetConfirmView, \
    PasswordResetDoneView, PasswordResetCompleteView, PasswordChangeDoneView
from django.urls import path

from account.forms import CustomPasswordResetForm, LoginForm
from account.views import RegistrationView, ActivateView, \
    RegistrationSuccessView, CustomLoginView, CustomLogoutView, \
    TwoFactorLoginView

urlpatterns = [
    path('login/',
         CustomLoginView.as_view(form_class=LoginForm),
         name='auth_login'),
    path('logout/',
         CustomLogoutView.as_view(),
         name='auth_logout'),
    path('login/step-2/<slug:uidb64>/<slug:utokenb64>/',
         TwoFactorLoginView.as_view(),
         name='auth_2fact_login'),

    # registration
    path('register/', RegistrationView.as_view(),
         name='registration_register'),
    path('register/success', RegistrationSuccessView.as_view(),
         name='registration_success'),
    path('activate/<slug:uidb64>/<slug:token>/',
         ActivateView.as_view(), name='activate'),

    # password reset
    path('reset/',
         PasswordResetView.as_view(form_class=CustomPasswordResetForm),
         name='auth_password_reset'),
    path('reset/done', PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/confirm/<slug:uidb64>/<slug:token>/',
         PasswordResetConfirmView.as_view(),
         name='auth_password_reset_confirm'),
    path('reset/complete/', PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),

    # password change
    path('change-password/', PasswordChangeView.as_view(),
         name='auth_password_change'),
    path('change-password/done/', PasswordChangeDoneView.as_view(),
         name='password_change_done'),
]
