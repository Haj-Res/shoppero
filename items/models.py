from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import SoftDeleteModel


class Item(SoftDeleteModel):
    """Items that are added to shopping lists"""
    name = models.CharField(_('item name'), max_length=200, db_index=True)
    code = models.CharField(_('item code'), max_length=20, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True,
                                validators=[MinValueValidator(0)])
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    tags = models.ManyToManyField('shopping_list.Category', blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'item'
        ordering = ('id',)

    def __str__(self):
        return self.name
