from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from rest_framework import serializers

from shopping_list.models import Item, ShoppingListItem, SharedShoppingList, \
    ShoppingList, Category


def item_to_dict(item: Item) -> dict:
    return {
        'id': item.id,
        'name': item.name,
        'code': item.code or '',
        'price': item.price or '',
        'tags': ', '.join([str(x) for x in item.tags.all()]),
        'url': reverse('api_item_single', args=[item.id])
    }


class ItemSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    tags_string = serializers.CharField(max_length=1000, allow_blank=True,
                                        default='')

    class Meta:
        model = Item
        fields = ('id', 'name', 'code', 'price', 'tags', 'tags_string')
        read_only_fields = ('id',)

    def create(self, validated_data):
        tags = validated_data.pop('tags_string', '').replace(', ', ',').split(
            ',')
        request = self.context['request']
        validated_data['user'] = request.user
        instance = super(ItemSerializer, self).create(validated_data)
        instance = self._add_tags(instance, tags)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags_string', '').replace(', ', ',').split(
            ',')
        instance = super(ItemSerializer, self).update(instance, validated_data)
        instance.tags.filter(~Q(name__in=tags)).all().delete()
        instance = self._add_tags(instance, tags)
        instance.save()
        return instance

    @classmethod
    def _add_tags(cls, instance, tags):
        for tag in tags:
            tag_query = Category.objects.filter(name=tag)
            if tag_query.exists():
                tag = tag_query.first()
            else:
                tag = Category.objects.create(name=tag)
            instance.tags.add(tag)
        return instance


class ShoppingListDetailsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    shopping_list__name = serializers.CharField(max_length=100)
    item_count = serializers.IntegerField()
    complete_item_count = serializers.IntegerField()
    total_price = serializers.FloatField()


class ShoppingListItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(required=False, allow_null=True)
    link_id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField(required=True, max_length=200)
    code = serializers.CharField(required=False, max_length=20,
                                 allow_blank=True)
    price = serializers.DecimalField(required=False, max_digits=9,
                                     decimal_places=2, default=None,
                                     min_value=0)
    quantity = serializers.DecimalField(required=False, max_digits=4,
                                        decimal_places=2, min_value=0,
                                        default=1)
    is_done = serializers.BooleanField(default=False)

    def validate(self, attrs):
        attrs = super(ShoppingListItemSerializer, self).validate(attrs)
        item_id = attrs.get('item_id')
        if item_id:
            exists = Item.objects.filter(pk=item_id).exists()
            if not exists:
                raise serializers.ValidationError({
                    'item_id': 'Invalid Item PK value'
                }, code='invalid')

        link_id = attrs.get('link_id')
        if link_id:
            exists = ShoppingListItem.objects \
                .filter(pk=link_id, deleted__isnull=True).exists()
            if not exists:
                raise serializers.ValidationError({
                    'link_id': 'Invalid ShoppingListItem PK value'
                }, code='invalid')
        return attrs


class ShoppingListSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, allow_blank=True)
    items = ShoppingListItemSerializer(many=True)
    emails = serializers.ListField(child=serializers.EmailField(), default=[])

    def validate(self, attrs):
        attrs = super(ShoppingListSerializer, self).validate(attrs)
        if len(attrs.get('items')) > 100:
            raise serializers.ValidationError(
                {'items': 'List can not contain more than 100 items'},
                code='invalid'
            )
        elif len(attrs.get('items')) < 1:
            raise serializers.ValidationError(
                {'items': 'List must contain at least one item'},
                code='invalid'
            )
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        instance = ShoppingList.objects.create(
            name=validated_data['name'],
            user=user
        )
        self._save_items(instance, validated_data['items'])
        self._save_emails(instance, validated_data['emails'])
        instance.save()
        return instance

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name')
        self._save_items(instance, validated_data.get('items'))
        self._save_emails(instance, validated_data.get('emails'))
        instance.save()
        return instance

    @classmethod
    def _save_emails(cls, instance, emails):
        shared_list = instance.sharedshoppinglist_set
        shared_list.filter(~Q(email__in=emails)).delete()
        for email in emails:
            exists = shared_list.filter(email=email).exists()
            if not exists:
                user = get_user_model().objects.filter(email=email).first()
                SharedShoppingList.objects.create(
                    shopping_list=instance,
                    user=user,
                    email=user.email if user else email
                )

    def _save_items(self, instance, items):
        request = self.context['request']
        user = request.user
        list_items = instance.shoppinglistitem_set
        link_ids = []
        for item in items:
            link_id = item.get('link_id')
            if link_id:
                link = list_items.get(pk=link_id)
                link.is_done = item['is_done']
                link.quantity = item['quantity']
                link.price = item['price']
                link.editor = user
                link.save()
            else:
                if not item.get('item_id'):
                    item_obj = Item.objects.create(
                        name=item['name'],
                        code=item['code'],
                        price=item['price'],
                        user=user
                    )
                    item_obj.save()
                else:
                    item_obj = Item.objects.get(pk=item.get('item_id'))
                link = ShoppingListItem.objects.create(
                    shopping_list=instance,
                    item=item_obj,
                    creator=user,
                    editor=user,
                    is_done=item['is_done'],
                    quantity=item['quantity'],
                    price=item['price']
                )
                link.save()
            link_ids.append(link.id)
        list_items.filter(~Q(id__in=link_ids)).delete()


class ItemAutocompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'name', 'code', 'price')
