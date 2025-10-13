from rest_framework import serializers
from .models import Order, OrderItem
from menu.models import MenuItem, MenuItemImage
import time
from users.models import Restaurant
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    price = serializers.DecimalField(max_digits=10, decimal_places=2, source='menu_item.price', read_only=True)
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    menu_item_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'menu_item_image', 'quantity', 'price']
        extra_kwargs = {'price': {'read_only': True}}

    def get_menu_item_image(self, obj):
        """Return first image URL of the menu item."""
        image_obj = obj.menu_item.images.first()
        return image_obj.image.url if image_obj else None

    def validate_menu_item(self, value):
        logger.debug(f"Validating menu_item ID: {value.id}, name: {value.name}, available: {value.is_available}, restaurant: {value.restaurant.name if value.restaurant else 'None'}")
        if not value.is_available:
            raise serializers.ValidationError(f"Menu item {value.name} is not available")
        if not value.restaurant:
            logger.error(f"Menu item {value.name} (ID: {value.id}) has no associated restaurant")
            raise serializers.ValidationError(f"Menu item {value.name} has no associated restaurant")
        return value

    def validate(self, data):
        logger.debug(f"Validating OrderItem data: {data}")
        return data

    def create(self, validated_data):
        logger.debug(f"Creating OrderItem with validated_data: {validated_data}")
        return OrderItem.objects.create(**validated_data)

    def to_representation(self, instance):
        """Convert Decimal fields to float for serialization."""
        ret = super().to_representation(instance)
        if 'price' in ret and isinstance(ret['price'], Decimal):
            ret['price'] = float(ret['price'])
        return ret

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    username = serializers.SerializerMethodField()
    restaurant = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all(), required=False)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    items_info = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'username', 'restaurant', 'restaurant_name', 'order_number',
            'subtotal', 'gst', 'service_charge', 'delivery_charge', 'total_amount',
            'payment_method', 'payment_status', 'status', 'reciver_name', 'street',
            'nearest_place', 'city', 'state', 'zip_code', 'mobile',
            'items', 'items_info', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'submenu': {'write_only': True, 'required': False, 'allow_null': True}
        }

    def get_username(self, obj):
        return obj.user.username if obj.user else None

    def validate_payment_method(self, value):
        valid_choices = [choice[0] for choice in Order.PAYMENT_METHOD_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f"\"{value}\" is not a valid choice.")
        return value

    def validate(self, data):
        logger.debug(f"Validating order data for user: {self.context['request'].user.username} (role: {self.context['request'].user.role}), data: {data}, partial: {self.partial}")
        
        if not self.partial:
            required_fields = ['reciver_name', 'street', 'city', 'state', 'zip_code', 'mobile']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({field: "This field is required."})
        
            if 'mobile' in data and (not data['mobile'].isdigit() or not (10 <= len(data['mobile']) <= 15)):
                raise serializers.ValidationError({"mobile": "Mobile number must be 10–15 digits."})

        for field in ['subtotal', 'gst', 'service_charge', 'delivery_charge', 'total_amount']:
            if field in data:
                try:
                    data[field] = float(data[field])
                    if data[field] < 0:
                        raise serializers.ValidationError({field: "Value cannot be negative."})
                except (ValueError, TypeError):
                    logger.error(f"Invalid value for {field}: {data[field]}")
                    raise serializers.ValidationError({field: f"Invalid value: {data[field]}"})

        if self.context['request'].user.role == 'customer' and not self.partial:
            items = data.get('items', [])
            if not items:
                logger.error("No items provided in order payload")
                raise serializers.ValidationError({"items": "At least one item is required for customer orders"})
            
            for index, item in enumerate(items):
                menu_item_id = item['menu_item'].id if hasattr(item['menu_item'], 'id') else item['menu_item']
                try:
                    menu_item = MenuItem.objects.get(id=menu_item_id)
                    if not menu_item.restaurant:
                        logger.error(f"Menu item {menu_item.name} (ID: {menu_item_id}) has no associated restaurant")
                        raise serializers.ValidationError({"items": f"Menu item ID {menu_item_id} at index {index} has no associated restaurant"})
                    logger.debug(f"Validated menu_item ID {menu_item_id} for item at index {index}")
                except MenuItem.DoesNotExist:
                    logger.error(f"Menu item ID {menu_item_id} not found for item at index {index}")
                    raise serializers.ValidationError({"items": f"Menu item ID {menu_item_id} at index {index} not found"})

            if not data.get('restaurant'):
                try:
                    first_menu_item = MenuItem.objects.get(id=items[0]['menu_item'].id)
                    data['restaurant'] = first_menu_item.restaurant
                    logger.debug(f"Inferred restaurant for customer order: {data['restaurant'].name} (ID: {data['restaurant'].id})")
                except MenuItem.DoesNotExist:
                    logger.error(f"Menu item ID {items[0]['menu_item'].id} not found for restaurant inference")
                    raise serializers.ValidationError({"items": f"Menu item ID {items[0]['menu_item'].id} not found for restaurant inference"})

            restaurant = data['restaurant']
            for index, item in enumerate(items):
                if item['menu_item'].restaurant != restaurant:
                    logger.error(f"Menu item {item['menu_item'].name} (ID: {item['menu_item'].id}) at index {index} does not belong to restaurant {restaurant.name} (ID: {restaurant.id})")
                    raise serializers.ValidationError({"items": f"Menu item {item['menu_item'].name} at index {index} does not belong to restaurant {restaurant.name}"})

        if self.context['request'].user.role == 'admin':
            try:
                restaurant = Restaurant.objects.get(user=self.context['request'].user)
                logger.debug(f"Admin restaurant: {restaurant.name} (ID: {restaurant.id})")
                if data.get('restaurant') and data['restaurant'] != restaurant:
                    logger.error(f"Restaurant mismatch: Provided {data.get('restaurant').name if data.get('restaurant') else None}, expected {restaurant.name}")
                    raise serializers.ValidationError({"restaurant": f"Admin can only create orders for their own restaurant: {restaurant.name}"})
                data['restaurant'] = restaurant
            except Restaurant.DoesNotExist:
                logger.error(f"No restaurant found for admin user {self.context['request'].user.username}")
                raise serializers.ValidationError({"restaurant": "No restaurant found for this admin"})

        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        logger.debug(f"Creating order with validated_data: {validated_data}, items: {items_data}")
        if not validated_data.get('order_number'):
            validated_data['order_number'] = f"ORD{int(time.time())}"
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            try:
                OrderItem.objects.create(
                    order=order,
                    menu_item=item_data['menu_item'],
                    quantity=item_data['quantity'],
                    price=item_data['menu_item'].price
                )
            except Exception as e:
                logger.error(f"Failed to create OrderItem for menu_item {item_data['menu_item'].id}: {str(e)}")
                raise serializers.ValidationError({"items": f"Failed to create item: {str(e)}"})
        logger.info(f"Order created successfully: #{order.order_number}, restaurant: {order.restaurant.name if order.restaurant else 'None'}")
        return order

    def to_representation(self, instance):
        """Convert Decimal fields to float for serialization."""
        ret = super().to_representation(instance)
        decimal_fields = ['subtotal', 'gst', 'service_charge', 'delivery_charge', 'total_amount']
        for field in decimal_fields:
            if field in ret and isinstance(ret[field], Decimal):
                ret[field] = float(ret[field])
        return ret