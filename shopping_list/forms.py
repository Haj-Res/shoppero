from django import forms
from django.utils.translation import gettext_lazy as _


class ItemListForm(forms.Form):
    item = forms.CharField(label=_('item'), max_length=100, required=True)
    quantity = forms.IntegerField(label=_('quantity'), min_value=0,
                                  max_value=32767, required=False)
    price = forms.DecimalField(label=_('item price'), max_digits=9,
                               decimal_places=2, required=False)


class ShoppingListForm(forms.ModelForm):
    class Meta:
        fields = ('name',)
