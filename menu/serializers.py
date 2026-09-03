from rest_framework import serializers
from .models import MenuItem, Category, MenuItemImage, Rating
import logging
from django.db.models import Avg

logger = logging.getLogger(__name__)

class MenuItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemImage
        fields = ['id', 'image']

class RestaurantSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()

class RatingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'rating', 'review', 'created_at', 'username']
        read_only_fields = ['created_at', 'username']

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    images = MenuItemImageSerializer(many=True, read_only=True)
    restaurant = RestaurantSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()
    ratings = RatingSerializer(many=True, read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'category', 'is_available', 'restaurant', 'images', 'average_rating', 'total_ratings', 'ratings']

    def get_average_rating(self, obj):
        ratings_list = [r.rating for r in obj.ratings.all()]
        if not ratings_list:
            return None
        return round(sum(ratings_list) / len(ratings_list), 1)

    def get_total_ratings(self, obj):
        return len(obj.ratings.all())

class MenuItemCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'category', 'is_available', 'images']
        read_only_fields = ['id']

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        if not images and 'request' in self.context:
            images = self.context['request'].FILES.getlist('images')
        
        logger.debug(f"Creating menu item with validated data: {validated_data}, images: {len(images)}")
        menu_item = MenuItem.objects.create(**validated_data)
        for image in images:
            try:
                MenuItemImage.objects.create(menu_item=menu_item, image=image)
            except Exception as e:
                logger.error(f"Error creating menu item image: {e}")
        return menu_item

    def update(self, instance, validated_data):
        images = validated_data.pop('images', None)
        if images is None and 'request' in self.context and 'images' in self.context['request'].FILES:
            images = self.context['request'].FILES.getlist('images')

        logger.debug(f"Updating menu item {instance.id} with validated data: {validated_data}")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if images is not None and len(images) > 0:
            MenuItemImage.objects.filter(menu_item=instance).delete()
            for image in images:
                try:
                    MenuItemImage.objects.create(menu_item=instance, image=image)
                except Exception as e:
                    logger.error(f"Error updating menu item image: {e}")
        return instance

    def to_representation(self, instance):
        return MenuItemSerializer(instance, context=self.context).data

class CategorySerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'items_count']

    def get_items_count(self, obj):
        if hasattr(obj, 'items_count'):
            return obj.items_count
        return getattr(obj, 'menu_items_count', None) or len(obj.menu_items.all())