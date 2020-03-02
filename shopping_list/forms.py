from django import forms

from shopping_list.models import Item


class ItemForm(forms.ModelForm):
    tags = forms.CharField(max_length=250, required=False)

    class Meta:
        model = Item
        fields = ('name', 'code', 'price', 'tags')

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.fields['tags'].widget = forms.Textarea()
        self.label_suffix = ''
