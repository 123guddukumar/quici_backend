from rest_framework import serializers
from .models import Wishlist, WishlistItem
from menu.serializers import MenuItemSerializer
from menu.models import MenuItem

class WishlistItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(), source='menu_item', write_only=True
    )

    class Meta:
        model = WishlistItem
        fields = ['id', 'menu_item', 'menu_item_id']

class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']