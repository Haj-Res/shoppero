import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, QueryDict
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView
from rest_framework.viewsets import ViewSet

from shopping_list.forms import ItemForm, ShoppingListForm, \
    ShoppingListItemForm, SharedShoppingListForm
from shopping_list.models import Item, ShoppingList
from shopping_list.querysets import get_shopping_list_items_queryset
from shopping_list.serializers import item_to_dict, \
    ShoppingListDetailsSerializer, ShoppingListSerializer, \
    ItemAutocompleteSerializer, ItemSerializer
from shopping_list.utils import tags_string_to_list, add_tag_to_item

logger = logging.getLogger('shoppero')


class ShoppingListView(TemplateView):
    template_name = 'shopping_list/shopping_lists.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ShoppingListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ShoppingListView, self).get_context_data(**kwargs)
        result = get_shopping_list_items_queryset(self.request.user.id)
        context.update({'shopping_lists': result})
        return context


class ShoppingListCreateView(TemplateView):
    template_name = 'shopping_list/shopping_list_create.html'
    list_form = ShoppingListForm
    shopping_list_item_form = ShoppingListItemForm
    item_form = ItemForm
    shared_list_form = SharedShoppingListForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ShoppingListCreateView, self).dispatch(request, *args,
                                                            **kwargs)


class ShoppingListSingle(View):
    template_name = 'shopping_list/shopping_list_create.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ShoppingListSingle, self).dispatch(request, *args,
                                                        **kwargs)

    def get_initial_context(self, pk):
        s_list = get_object_or_404(ShoppingList, pk=pk, user=self.request.user,
                                   deleted__isnull=True)
        return {'list': s_list}

    def get(self, request, pk):
        context = self.get_initial_context(pk)
        rendered = render(request, self.template_name, context)
        return HttpResponse(rendered)

    def patch(self, request, pk):
        item = get_object_or_404(ShoppingList, pk=pk, user=request.user,
                                 deleted__isnull=True)
        item.soft_delete()
        result = get_shopping_list_items_queryset(request.user.id)
        serializer = ShoppingListDetailsSerializer(result, many=True)
        data = serializer.data
        for i in range(0, len(data)):
            data[i]['url'] = reverse('shopping_list_single',
                                     args=[data[i]['id']])
        return JsonResponse({'status': 'success', 'content': data})

    def delete(self, request, pk):
        item = get_object_or_404(ShoppingList, pk=pk, user=request.user,
                                 deleted__isnull=True)
        item.delete()
        result = get_shopping_list_items_queryset(request.user.id)
        serializer = ShoppingListDetailsSerializer(result, many=True)
        data = serializer.data
        for i in range(0, len(data)):
            data[i]['url'] = reverse('shopping_list_single',
                                     args=[data[i]['id']])
        return JsonResponse({'status': 'success', 'content': data})


class SingleItemJsonView(View):
    _form_class = ItemForm
    _serializer = ItemSerializer

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SingleItemJsonView, self).dispatch(request, *args,
                                                        **kwargs)

    def get(self, request, pk, *args, **kwargs):
        logger.info('User %d requesting item %d', request.user.id, pk)
        item = get_object_or_404(Item, pk=pk)
        serializer = self._serializer(item)
        url = reverse('item_single', args=[item.pk])
        context = {'status': 'success', 'item': serializer.data, 'url': url}
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


class ItemAutocompleteView(View):
    _serializer = ItemAutocompleteSerializer

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ItemAutocompleteView, self).dispatch(request, *args,
                                                          **kwargs)

    def get(self, request):
        name = request.GET.get('name', '')
        if len(name) < 2:
            return JsonResponse([], status=200)
        items = Item.objects.filter(name__icontains=name,
                                    deleted__isnull=True).all()
        serializer = self._serializer(items, many=True)
        return JsonResponse(serializer.data, safe=False)


class ShoppingListViewSet(ViewSet):
    _serializer = ShoppingListSerializer

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ShoppingListViewSet, self).dispatch(request, *args,
                                                         **kwargs)

    def create(self, request):
        logger.info(f'User {request.user} creating a new list')
        logger.info(request.data)
        serializer = self._serializer(data=request.data,
                                      context={'request': request})
        if serializer.is_valid():
            messages.success(request, _('List saved'))
            instance = serializer.save()
            return JsonResponse({
                'status': 'success',
                'url': reverse('shopping_list_single', args=[instance.pk]),
                'content': serializer.data
            })
        else:
            logger.info(serializer.errors)
            messages.error(request, _('List not saved'))
            return JsonResponse({
                'status': 'error',
                'content': serializer.errors
            })

    def update(self, request, pk):
        logger.info(f'User {request.user} updating list {pk}')
        logger.info(request.data)
        instance = get_object_or_404(ShoppingList, pk=pk, deleted__isnull=True)
        serializer = self._serializer(instance, data=request.data,
                                      context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({
                'status': 'success',
                'url': reverse('shopping_list')
            })
        else:
            logger.info(serializer.errors)
            return JsonResponse({
                'status': 'error',
                'content': serializer.errors
            })
