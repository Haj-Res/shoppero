from django import forms

from shopping_list.models import ShoppingList, ShoppingListItem, \
    SharedShoppingList


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
