from django.db.models import Count, Sum, F, FloatField, Q
from django.views.generic import TemplateView

from shopping_list.models import ShoppingListItem


class ShoppingListView(TemplateView):
    template_name = 'shopping_list/list.html'

    def get_context_data(self, **kwargs):
        context = super(ShoppingListView, self).get_context_data(**kwargs)
        result = ShoppingListItem.objects.values(
            'shopping_list__name'
        ).filter(
            shopping_list__user_id=self.request.user.id,
        ).annotate(
            id=F('shopping_list_id'),
            item_count=Count('item'),
            complete_item_count=Count('item', filter=Q(is_done=True)),
            total_price=Sum(
                F('item__price') * F('quantity'), output_field=FloatField()
            ),
        )
        print(result.query)
        context.update({'shopping_lists': result})
        return context
