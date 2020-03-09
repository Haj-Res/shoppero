from rest_framework import serializers


class ShoppingListItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    shopping_list__name = serializers.CharField(max_length=100)
    item_count = serializers.IntegerField()
    complete_item_count = serializers.IntegerField()
    total_price = serializers.FloatField()
