import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import FormView, TemplateView

from account.forms import SignUpForm
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
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            logger.error(str(e))
            user = None
        if user is not None \
                and account_activation_token.check_token(user, token):
            User.objects.filter(pk=user.id).update(is_active=True)
            # user.is_active = True
            # user.save()
            user.refresh_from_db()
            logger.info('User %s activated', user)
            return render(request, 'registration/activation_complete.html')
        else:
            logger.info('Activation failed')
            return render(self.request, 'registration/activate.html')
