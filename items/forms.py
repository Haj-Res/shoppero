from django import forms
from django.utils.translation import ugettext as _

from items.models import Item


class ItemForm(forms.ModelForm):
    tags = forms.CharField(max_length=250, required=False)

    class Meta:
        model = Item
        fields = ('name', 'code', 'price', 'tags')

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['tags'].widget = forms.Textarea()
        self.fields['tags'].widget.attrs['placeholder'] = _(
            'Add your tags separated with a coma. Example: desert,sweet,fruit'
        )
        self.fields['tags'].widget.attrs['cols'] = 2
