from django.urls import path

from shopping_list.views import ShoppingListView, ItemListView, \
    SingleItemJsonView, ItemAutocompleteView, ShoppingListCreateView

urlpatterns = [
    path('', ShoppingListView.as_view(), name='shopping_list'),
    path('create/', ShoppingListCreateView.as_view(),
         name='shopping_list_create'),
    path('items/', ItemListView.as_view(), name='items'),
    path('items/<int:pk>/', SingleItemJsonView.as_view(), name='item_single'),
    path('items/autocomplete/', ItemAutocompleteView.as_view(),
         name='item_autocomplete')
]
