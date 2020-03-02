from django.urls import path

from shopping_list.views import ShoppingListView, ItemListView, \
    SingleItemJsonView

urlpatterns = [
    path('', ShoppingListView.as_view(), name='shopping_list'),
    path('items/', ItemListView.as_view(), name='items'),
    path('items/<int:pk>/', SingleItemJsonView.as_view(), name='item_single'),
]
