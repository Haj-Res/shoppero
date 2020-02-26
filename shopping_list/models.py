from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import SoftDeleteModel


class Item(SoftDeleteModel):
    """Items that are added to shopping lists"""
    name = models.CharField(max_length=200)
    code = models.CharField(_('item code'), max_length=20, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, null=True,
                                blank=True)
    tags = models.ManyToManyField('shopping_list.Category', blank=True)

    class Meta:
        db_table = 'item'

    def __str__(self):
        return self.name


class ShoppingList(SoftDeleteModel):
    """Shopping list object"""
    name = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    created = models.DateTimeField(_('creation date'), auto_created=True)
    items = models.ManyToManyField('shopping_list.Item',
                                   through='ShoppingListItem')

    class Meta:
        db_table = 'shopping_list'

    def __str__(self):
        return self.name


class ShoppingListItem(SoftDeleteModel):
    """Object for connecting items and shopping lists"""
    shopping_list = models.ForeignKey(ShoppingList,
                                      on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='creator')
    editor = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.SET_NULL,
                               null=True, related_name='editor')
    is_done = models.BooleanField(default=False)
    quantity = models.PositiveSmallIntegerField(default=1)
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    class Meta:
        db_table = 'shared_shopping_list'

    def __str__(self):
        return f'{self.user.name} - {self.shopping_list.name}'


class Category(SoftDeleteModel):
    name = models.CharField(_('item category'), max_length=30)
