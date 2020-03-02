from django.urls import reverse

from shopping_list.models import Item


def item_to_dict(item: Item) -> dict:
    return {
        'id': item.id,
        'name': item.name,
        'code': item.code or '',
        'price': item.price or '',
        'tags': ', '.join([str(x) for x in item.tags.all()]),
        'url': reverse('item_single', args=[item.id])
    }
