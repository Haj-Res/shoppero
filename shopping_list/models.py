import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from core.models import SoftDeleteModel
from utils.send_mail import send_mail

logger = logging.getLogger('shoppero')


class Item(SoftDeleteModel):
    """Items that are added to shopping lists"""
    name = models.CharField(_('item name'), max_length=200)
    code = models.CharField(_('item code'), max_length=20, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, null=True,
                                blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    tags = models.ManyToManyField('shopping_list.Category', blank=True)

    class Meta:
        db_table = 'item'

    def __str__(self):
        return self.name

    def clean_fields(self, exclude=None):
        super(Item, self).clean_fields(exclude)
        if self.price and self.price < 0:
            raise ValidationError({
                'price': _('Price must be a positive number')
            }, code='invalid')


class ShoppingList(SoftDeleteModel):
    """Shopping list object"""
    name = models.CharField(_('shopping list name'), max_length=100,
                            blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    created = models.DateTimeField(_('creation date'), auto_now_add=True)
    items = models.ManyToManyField('shopping_list.Item',
                                   through='ShoppingListItem')

    class Meta:
        db_table = 'shopping_list'

    def __str__(self):
        return self.name


class ShoppingListItem(SoftDeleteModel):
    """Object for connecting items and shopping lists"""
    shopping_list = models.ForeignKey(ShoppingList, null=True,
                                      on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                on_delete=models.CASCADE,
                                related_name='creator')
    editor = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.SET_NULL,
                               null=True, related_name='editor')
    is_done = models.BooleanField(default=False)
    quantity = models.DecimalField(max_digits=4, decimal_places=2, default=1,
                                   validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=9, decimal_places=2, null=True,
                                blank=True)

    class Meta:
        db_table = 'shopping_list_item'

    def __str__(self):
        return f'{self.shopping_list.name} : {self.item.name}'

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.item.price
        super(ShoppingListItem, self).save(*args, **kwargs)


class SharedShoppingList(SoftDeleteModel):
    shopping_list = models.ForeignKey(ShoppingList,
                                      on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)

    class Meta:
        db_table = 'shared_shopping_list'

    def __str__(self):
        return f'{self.get_email()} - {self.shopping_list.name}'

    def get_email(self):
        if self.email:
            return self.email
        else:
            return self.user.email


class Category(SoftDeleteModel):
    name = models.CharField(_('item category'), max_length=30)

    def __str__(self):
        return self.name


@receiver(post_save, sender=SharedShoppingList)
def share_shopping_list_signal(sender, instance, created, **kwargs):
    """Inform user via mail that someone shared a list with them"""
    logger.info('Sending mail for shared list')
    if created:
        list_owner = instance.shopping_list.user
        if instance.user:
            email = instance.user.email
        else:
            email = instance.email
        # TODO replace placeholder url with proper url leading to list
        url = '#'
        subject = _('New shared shopping list')
        message = render_to_string('mail/shared_list.html', {
            'email': email,
            'sender': list_owner,
            'list_url': url
        })
        send_mail(subject, message, [email])
