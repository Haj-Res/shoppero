import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, resolve_url
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import FormView, TemplateView

from account.forms import SignUpForm, TwoFactorForm
from account.models import Security
from account.tokens import account_activation_token
from core import string_constants

User = get_user_model()
logger = logging.getLogger('shoppero')


class RegistrationView(FormView):
    """Registration FormView for user account registration"""
    template_name = 'registration/registration_form.html'
    form_class = SignUpForm
    success_url = reverse_lazy('registration_success')

    def form_valid(self, form):
        user = form.save()
        user.refresh_from_db()
        user.profile.first_name = form.cleaned_data.get('first_name')
        user.profile.last_name = form.cleaned_data.get('last_name')
        user.save()
        logger.info('User %s registered', user)
        domain = get_current_site(self.request).domain
        subject = str(string_constants.ACTIVATE_ACCOUNT_SUBJECT)
        message = render_to_string('registration/activation_email.html', {
            'user': user,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
            'expiration_days': settings.PASSWORD_RESET_TIMEOUT_DAYS
        })
        user.email_user(subject, message)
        logger.info('Sent activation email to %s', user.email)
        return super(RegistrationView, self).form_valid(form)


class RegistrationSuccessView(TemplateView):
    template_name = 'registration/registration_complete.html'


class ActivateView(View):
    """Class view for user account activation"""

    def get(self, request, uidb64, token):
        logger.info('Activation request for %s/%s', uidb64, token)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            logger.error(str(e))
            user = None
        if user is not None \
                and account_activation_token.check_token(user, token):
            User.objects.filter(pk=user.id).update(is_active=True)
            user.refresh_from_db()
            logger.info('User %s activated', user)
            return render(request, 'registration/activation_complete.html')
        else:
            logger.info('Activation failed')
            return render(self.request, 'registration/activate.html')


class CustomLoginView(LoginView):
    def form_valid(self, form):
        res = super(CustomLoginView, self).form_valid(form)
        user = self.request.user
        has_security = False
        try:
            has_security = user.security is not None
        except Exception as e:
            logger.error(str(e))
        if not has_security:
            Security.objects.create(user=user)
            user.security.save()
        if user.security.two_factor:
            user.security.generate_token()
            token_2 = user.security.token_2
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            utokenb64 = urlsafe_base64_encode(force_bytes(token_2))
            logout(self.request)
            return redirect('auth_2fact_login', uidb64=uidb64,
                            utokenb64=utokenb64)
        return res


class CustomLogoutView(TemplateView):
    template_name = 'registration/login.html'
    extra_context = None

    @method_decorator(never_cache)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, 'Logged out')
        return super(CustomLogoutView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        super(CustomLogoutView, self).get(request, *args, **kwargs)
        return redirect('auth_login')


class TwoFactorLoginView(View):
    template_name = 'registration/two_factor.html'
    form_class = TwoFactorForm

    def get(self, request, uidb64=None, utokenb64=None):
        pk = force_str(urlsafe_base64_decode(uidb64))
        if not get_user_model().objects.filter(pk=pk).exists():
            return redirect('auth_login')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, uidb64=None, utokenb64=None):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            pk = force_str(urlsafe_base64_decode(uidb64))
            token_2 = force_str(urlsafe_base64_decode(utokenb64))
            try:
                user = User.objects.get(pk=pk)
                token = form.cleaned_data['token']
                if user.security.is_token_valid(token, token_2):
                    login(request, user)
                    redirect_url = resolve_url(settings.LOGIN_REDIRECT_URL)
                else:
                    user.security.login_attempts += 1
                    user.security.save()
                    messages.error(request, 'Invalid authentication code')
                    return render(request, self.template_name, {'form': form})
            except User.DoesNotExist:
                messages.error(request, 'Submission error')
                redirect_url = resolve_url('auth_login')
            return redirect(redirect_url)
