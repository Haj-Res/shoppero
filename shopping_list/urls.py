from django.urls import path

from shopping_list.views import ShoppingListView, ItemListView, \
    ShoppingListCreateView, ShoppingListSingle

urlpatterns = [
    path('lists/', ShoppingListView.as_view(), name='shopping_list'),
    path('lists/create/', ShoppingListCreateView.as_view(),
         name='shopping_list_create'),
    path('lists/<int:pk>/', ShoppingListSingle.as_view(),
         name='shopping_list_single'),
    path('items/', ItemListView.as_view(), name='items')
]
