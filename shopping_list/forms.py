from django import forms

from shopping_list.models import Item, ShoppingList, ShoppingListItem, \
    SharedShoppingList


class ItemForm(forms.ModelForm):
    tags = forms.CharField(max_length=250, required=False)

    class Meta:
        model = Item
        fields = ('name', 'code', 'price', 'tags')

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.fields['tags'].widget = forms.Textarea()
        self.label_suffix = ''


class ShoppingListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(ShoppingListForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''


class ShoppingListItemForm(forms.ModelForm):
    class Meta:
        model = ShoppingListItem
        fields = ('item', 'is_done', 'quantity', 'price')

    def __init__(self, *args, **kwargs):
        super(ShoppingListItemForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''


class SharedShoppingListForm(forms.ModelForm):
    class Meta:
        model = SharedShoppingList
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SharedShoppingListForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''
