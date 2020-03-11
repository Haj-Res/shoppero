import logging
from collections import Iterable

from shopping_list.models import Category, Item

logger = logging.getLogger('shoppero')


def add_tag_to_item(instance, tag_list):
    for t in tag_list:
        tag_query = Category.objects.filter(name=t)
        if tag_query.exists():
            tag = tag_query.all()[0]
        else:
            tag = Category.objects.create(name=t)
        try:
            instance.tags.add(tag)
        except Exception as e:
            logger.exception(e)
    instance.save()
    return instance


def tags_string_to_list(tags_string: str) -> Iterable:
    return [x.strip() for x in tags_string.split(',')]


def get_item_by_name(name, user=None):
    item = Item.objects.filter(deleted__isnull=True, name=name)
    if user:
        item = item.filter(user=user)
    return item.first()
