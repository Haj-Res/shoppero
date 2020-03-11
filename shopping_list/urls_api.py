from django.urls import path

from shopping_list.views import ShoppingListViewSet

urlpatterns = [
    path('lists/', ShoppingListViewSet.as_view({'post': 'create'}),
         name='api_shopping_list_create'),
    path('lists/<int:pk>/',
         ShoppingListViewSet.as_view({'put': 'update'}),
         name='api_shopping_list_single')
]
