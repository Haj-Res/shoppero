from django.contrib import admin

from shopping_list import models

admin.site.register(models.Item)
admin.site.register(models.ShoppingList)
admin.site.register(models.ShoppingListItem)
admin.site.register(models.SharedShoppingList)
