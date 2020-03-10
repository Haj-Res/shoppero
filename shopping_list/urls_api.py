from django.urls import path

from shopping_list.views import UpdateShoppingListViewSet

urlpatterns = [
    path('lists/<int:pk>/',
         UpdateShoppingListViewSet.as_view({'put': 'update'}),
         name='api_shopping_list_single')
]
