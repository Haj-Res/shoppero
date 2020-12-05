from django.views.generic import ListView

from items.forms import ItemForm
from items.models import Item


class ItemListView(ListView):
    model = Item
    template_name = 'items/item_list.html'
    queryset = Item.objects.filter(deleted__isnull=True)
    ordering = ('id',)

    form = ItemForm

    def get_queryset(self):
        qs = super(ItemListView, self).get_queryset()
        return qs.filter(user=self.request.user).all()

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(ItemListView, self).get_context_data(object_list=object_list, **kwargs)
        ctx['form'] = self.form()
        return ctx
