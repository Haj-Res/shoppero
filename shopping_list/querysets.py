from django.db.models import F, Count, Sum, Q, FloatField, QuerySet

from shopping_list.models import ShoppingListItem


def get_shopping_list_items_queryset(user_id: int) -> QuerySet:
    """
    A query for getting shopping list details for the shopping lists overview
    :param user_id: user's ID
    :return: a queryset
    """
    return ShoppingListItem.objects.values(
        'shopping_list__name'
    ).filter(
        shopping_list__user_id=user_id,
        shopping_list__deleted__isnull=True,
    ).annotate(
        id=F('shopping_list_id'),
        item_count=Count('item'),
        complete_item_count=Count('item', filter=Q(is_done=True)),
        total_price=Sum(
            F('item__price') * F('quantity'), output_field=FloatField()
        ),
    ).order_by('shopping_list__id')
