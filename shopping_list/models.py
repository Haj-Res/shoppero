import logging

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from account.models import Profile, User
from core.models import SoftDeleteModel
from items.models import Item
from utils.send_mail import send_mail

logger = logging.getLogger('shoppero')


class ShoppingList(SoftDeleteModel):
    """Shopping list object"""
    name = models.CharField(_('shopping list name'), max_length=100,
                            blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    created = models.DateTimeField(_('creation date'), auto_now_add=True)

    class Meta:
        db_table = 'shopping_list'

    def __str__(self):
        return self.name


class ShoppingListItem(models.Model):
    """Object for connecting items and shopping lists"""
    shopping_list = models.ForeignKey(ShoppingList, null=True, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name='creator')
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='editor')
    is_done = models.BooleanField(default=False)
    quantity = models.DecimalField(max_digits=4, decimal_places=2, default=1, validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True,
                                validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'shopping_list_item'

    def __str__(self):
        return f'{self.shopping_list.name} : {self.item.name}'


class SharedShoppingList(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField(null=True, blank=True)
    access_level = models.CharField(choices=Profile.SHARE_LEVEL_CHOICES, default=Profile.READ_ACCESS, max_length=10)

    class Meta:
        db_table = 'shared_shopping_list'

    def __str__(self):
        return f'{self.get_email()} - {self.shopping_list.name}'

    def get_email(self):
        if self.user:
            return self.user.email
        return self.email


class Category(SoftDeleteModel):
    name = models.CharField(_('item category'), max_length=30)

    def __str__(self):
        return self.name


@receiver(post_save, sender=SharedShoppingList)
def share_shopping_list_signal(sender, instance: SharedShoppingList, created, **kwargs):
    """Inform user via mail that someone shared a list with them"""
    logger.info('Sending mail for shared list')
    if created:
        list_owner = instance.shopping_list.user
        email = instance.get_email()
        # TODO replace placeholder url with proper url leading to list
        url = reverse('shopping_list_single', args=[instance.shopping_list.id])
        subject = _('New shared shopping list')
        message = render_to_string('mail/shared_list.html', {
            'email': email,
            'sender': list_owner,
            'list_url': url
        })
        send_mail(subject, message, [email])
