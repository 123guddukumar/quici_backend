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
        avg = obj.ratings.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else None

    def get_total_ratings(self, obj):
        return obj.ratings.count()

class MenuItemCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'category', 'is_available', 'images']

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        logger.debug(f"Creating menu item with validated data: {validated_data}, images: {len(images)}")
        menu_item = MenuItem.objects.create(**validated_data)
        for image in images:
            MenuItemImage.objects.create(menu_item=menu_item, image=image)
        return menu_item

    def update(self, instance, validated_data):
        images = validated_data.pop('images', None)
        logger.debug(f"Updating menu item {instance.id} with validated data: {validated_data}")
        
        # Update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update images if provided
        if images is not None:
            # Clear existing images
            MenuItemImage.objects.filter(menu_item=instance).delete()
            # Add new images
            for image in images:
                MenuItemImage.objects.create(menu_item=instance, image=image)
        
        return instance

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']