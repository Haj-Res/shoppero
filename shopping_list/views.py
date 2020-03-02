import logging
from collections import Iterable

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, F, FloatField, Q
from django.http import HttpResponse, JsonResponse, QueryDict
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from shopping_list.forms import ItemForm
from shopping_list.models import ShoppingListItem, Item, Category
from shopping_list.serializer import item_to_dict

logger = logging.getLogger('shoppero')


class ShoppingListView(TemplateView):
    template_name = 'shopping_list/shopping_lists.html'

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
        context.update({'shopping_lists': result})
        return context


class SingleItemJsonView(View):
    _form_class = ItemForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SingleItemJsonView, self).dispatch(request, *args,
                                                        **kwargs)

    def get(self, request, pk, *args, **kwargs):
        logger.info('User %d requesting item %d', request.user.id, pk)
        item = get_object_or_404(Item, pk=pk)
        context = {'status': 'success', 'item': item_to_dict(item)}
        return JsonResponse(context, safe=False)

    def delete(self, request, pk):
        logger.info('User %d deleting item %d', request.user.id, pk)
        instance = get_object_or_404(Item, id=pk, user=request.user)
        instance.soft_delete()
        instance.save()
        context = {'status': 'success', 'message': _('Item deleted')}
        return JsonResponse(context)

    def patch(self, request, pk):
        logger.info('User %d updating item %d', request.user.id, pk)
        instance = get_object_or_404(Item, id=pk, user=request.user)
        data = QueryDict(request.body)
        logger.info(data)
        form = self._form_class(data or None, instance=instance)
        if form.is_valid():
            tags = form.cleaned_data.pop('tags', '')
            instance = form.save()
            tag_list = tags_string_to_list(tags)
            instance.tags.filter(~Q(name__in=tag_list)).all().delete()
            instance = add_tag_to_item(instance, tag_list)
            instance.refresh_from_db()
            context = {
                'status': 'success',
                'message': _('Item updated'),
                'content': item_to_dict(instance)
            }
        else:
            logger.info('Item update failed: %s', form.errors)
            context = {
                'status': 'error',
                'message': _('Submission error'),
                'content': form.errors
            }
        return JsonResponse(context, safe=False)


class ItemListView(View):
    _template_name = 'shopping_list/item_list.html'
    _form_class = ItemForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ItemListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        logger.info('User %d requesting item list', request.user.id)
        order_param = request.GET.get('order_by', 'id')
        items = Item.objects.filter(deleted__isnull=True).all().order_by(
            order_param)
        context = {'items': items}
        return HttpResponse(render(request, self._template_name, context))

    def post(self, request):
        logger.info('Creating new item for user %d', request.user.id)
        logger.info(request.POST)
        form = self._form_class(request.POST)
        if form.is_valid():
            tags = form.cleaned_data.pop('tags', '')
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            tag_list = tags_string_to_list(tags)
            instance = add_tag_to_item(instance, tag_list)
            instance.refresh_from_db()
            context = {
                'status': 'success',
                'message': _('Item created'),
                'content': item_to_dict(instance)
            }
        else:
            logger.info('Item creation failed: %s', form.errors)
            context = {
                'status': 'error',
                'message': _('Submission error'),
                'content': form.errors
            }
        return JsonResponse(context, safe=False)


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
