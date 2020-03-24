from django.urls import path

from shopping_list.views import ShoppingListViewSet, ItemViewSet

urlpatterns = [
    path('lists/',
         ShoppingListViewSet.as_view({'post': 'create'}),
         name='api_shopping_list_create'),
    path('lists/<int:pk>/',
         ShoppingListViewSet.as_view({
             'put': 'update',
             'patch': 'archive',
             'delete': 'delete'
         }),
         name='api_shopping_list_single'),
    path('items/',
         ItemViewSet.as_view({
             'get': 'list',
             'post': 'create'
         }),
         name='api_items_list'),
    path('items/<int:pk>/',
         ItemViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'archive',
         }),
         name='api_item_single'),
    path('items/autocomplete/',
         ItemViewSet.as_view({
             'get': 'autocomplete'
         }),
         name='api_item_autocomplete')
]
