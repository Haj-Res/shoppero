import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, QueryDict
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView
from querystring_parser import parser

from shopping_list.forms import ItemForm, ShoppingListForm, \
    ShoppingListItemForm, SharedShoppingListForm
from shopping_list.models import Item, ShoppingList
from shopping_list.querysets import get_shopping_list_items_queryset
from shopping_list.serializer import item_to_dict
from shopping_list.serializers import ShoppingListItemSerializer
from shopping_list.utils import tags_string_to_list, add_tag_to_item, \
    get_item_by_name

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


class ShoppingListCreateView(View):
    template_name = 'shopping_list/shopping_list_create.html'
    list_form = ShoppingListForm
    shopping_list_item_form = ShoppingListItemForm
    item_form = ItemForm
    shared_list_form = SharedShoppingListForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ShoppingListCreateView, self).dispatch(request, *args,
                                                            **kwargs)

    def get_context_data(self, **kwargs):
        list_form = self.list_form()
        item_form = self.shopping_list_item_form()
        return {'list_form': list_form, 'item_form': item_form}

    def get(self, request, pk=None):
        context = self.get_context_data(pk=pk)
        return HttpResponse(render(request, self.template_name, context))

    def post(self, request):
        logger.info('User creating list')
        logger.info(request.POST)
        data = parser.parse(request.POST.urlencode())
        shopping_list = data.get('shopping_list')
        list_form = self.list_form(shopping_list)
        if list_form.is_valid():
            s_list = list_form.save(commit=False)
            s_list.user = request.user
            items_dict = data.get('items')
            if not items_dict:
                return JsonResponse({
                    'status': 'error',
                    'message': 'List must have at least one item'
                })
            s_list.save()
            for __, item_dict in items_dict.items():
                item_name = item_dict.pop('item')
                item = get_item_by_name(item_name, request.user)
                if not item:
                    item_dict['name'] = item_name
                    i_form = self.item_form(item_dict)
                    if i_form.is_valid():
                        item_obj = i_form.save(commit=False)
                        item_obj.user = request.user
                        item_obj.save()
                        item = item_obj.id
                    else:
                        logger.error(i_form.errors)
                item_dict['item'] = item
                item_form = self.shopping_list_item_form(item_dict)
                if item_form.is_valid():
                    item_form.cleaned_data['shopping_list'] = s_list.id
                    shopping_list_items = item_form.save(commit=False)
                    shopping_list_items.shopping_list = s_list
                    shopping_list_items.save()
                else:
                    logger.error(item_form.errors)
            share_list = data.get('emails')
            mail_list = share_list['']
            if not isinstance(mail_list, list):
                mail_list = [mail_list]
            for mail in mail_list:
                if mail == '':
                    continue
                shared_list_dict = {
                    'shopping_list': s_list.id,
                    'email': mail
                }

                try:
                    user = get_user_model().objects.get(email=mail)
                    shared_list_dict['user'] = user.id
                except get_user_model().DoesNotExist:
                    pass
                shared_list_form = self.shared_list_form(shared_list_dict)
                if shared_list_form.is_valid():
                    share = shared_list_form.save()
                else:
                    logger.error(shared_list_form.errors)

            messages.success(request, _('Shopping list created'))
            return JsonResponse(
                {'status': 'success', 'url': reverse('shopping_list')})
        else:
            errors = {}
            for field in list_form:
                if field.errors:
                    errors.update({field.name: [field.errors.as_text()[2:]]})
            logger.error(errors)
            context = {'status': 'error', 'errors': errors}
            return JsonResponse(context, safe=False)


class ShoppingListSingle(View):
    template_file = 'shopping_list/shopping_list_create.html'

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
        rendered = render(request, self.template_file, context)
        return HttpResponse(rendered)

    def patch(self, request, pk):
        item = get_object_or_404(ShoppingList, pk=pk, user=request.user,
                                 deleted__isnull=True)
        item.soft_delete()
        result = get_shopping_list_items_queryset(request.user.id)
        serializer = ShoppingListItemSerializer(result, many=True)
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
        serializer = ShoppingListItemSerializer(result, many=True)
        data = serializer.data
        for i in range(0, len(data)):
            data[i]['url'] = reverse('shopping_list_single',
                                     args=[data[i]['id']])
        return JsonResponse({'status': 'success', 'content': data})


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


class ItemAutocompleteView(View):
    @method_decorator(login_required)
    def get(self, request):
        name = request.GET.get('name', '')
        if len(name) < 2:
            return JsonResponse(status=200, safe=False,
                                data={'status': 'success', 'content': []})
        items = Item.objects.filter(
            name__icontains=name
        ).exclude(
            deleted__isnull=False
        ).values('name', 'code', 'price').all().order_by('name')[:10]
        return JsonResponse([x for x in items], safe=False)
