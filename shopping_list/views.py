import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet, ModelViewSet

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


class ShoppingListViewSet(ViewSet):
    _serializer = ShoppingListSerializer
    _serializer_details = ShoppingListDetailsSerializer

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
            messages.success(request, _('Shopping list update'))
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

    def archive(self, request, pk):
        logger.info(u'User %d archiving list %d', request.user.id, pk)
        item = get_object_or_404(ShoppingList, pk=pk, user=request.user,
                                 deleted__isnull=True)
        item.soft_delete()
        result = get_shopping_list_items_queryset(request.user.id)
        serializer = self._serializer_details(result, many=True)
        data = serializer.data
        for i in range(0, len(data)):
            data[i]['url'] = reverse('api_shopping_list_single',
                                     args=[data[i]['id']])
        return JsonResponse({'status': 'success', 'content': data})

    def delete(self, request, pk, ):
        logger.info(u'User %d deleting list %d', request.user.id, pk)
        item = get_object_or_404(ShoppingList, pk=pk, user=request.user,
                                 deleted__isnull=True)
        item.delete()
        result = get_shopping_list_items_queryset(request.user.id)
        serializer = self._serializer_details(result, many=True)
        data = serializer.data
        for i in range(0, len(data)):
            data[i]['url'] = reverse('api_shopping_list_single',
                                     args=[data[i]['id']])
        return JsonResponse({'status': 'success', 'content': data})


class ItemViewSet(ModelViewSet):
    serializer_class = ItemSerializer
    autocomplete_serializer_class = ItemAutocompleteSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.item_set.filter(deleted__isnull=True).all()

    def get_serializer_context(self):
        context = super(ItemViewSet, self).get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(detail=True, method=['patch'])
    def archive(self, request, pk=None):
        logger.info('User %d deleting item %d', request.user.id, pk)
        instance = self.get_object()
        instance.soft_delete()
        instance.save()
        context = {'status': 'success', 'message': _('Item deleted')}
        return JsonResponse(context)

    def update(self, request, *args, **kwargs):
        logger.info('User %d updating item %d', request.user.pk, args[0])
        res = super(ItemViewSet, self).update(request, *args, **kwargs)
        res.data.update({
            'url': reverse('api_item_single', args=[res.data['id']])
        })
        return res

    def create(self, request, *args, **kwargs):
        logger.info('User %d creating item %s', request.user.pk, request.data)
        res = super(ItemViewSet, self).create(request, *args, **kwargs)
        res.data.update({
            'url': reverse('api_item_single', args=[res.data['id']])
        })
        return res

    def autocomplete(self, request):
        name = request.GET.get('name', '')
        if len(name) < 2:
            return JsonResponse([], status=200)
        items = Item.objects.filter(name__icontains=name,
                                    deleted__isnull=True).all()
        serializer = self.autocomplete_serializer_class(items, many=True)
        return JsonResponse(serializer.data, safe=False)
