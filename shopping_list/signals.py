from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from shopping_list.models import SharedShoppingList


@receiver(post_save, sender=SharedShoppingList)
def share_shopping_list_signal(sender, instance, created, **kwargs):
    """Inform user via mail that someone shared a list with them"""
    if created:
        list_owner = instance.shopping_list.user
        user = instance.user
        # TODO replace placeholder url with proper url leading to list
        url = '#'
        subject = _('New shared shopping list')
        message = render_to_string('mail/shared_list.html', {
            'user': user,
            'sender': list_owner,
            'list_url': url
        })
        user.email_user(subject, message)
