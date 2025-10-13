from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, Restaurant, City, Address

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'nearest_place', 'city', 'state', 'zip_code', 'mobile_number', 'is_default', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        if not data.get('street') or not data.get('city') or not data.get('state') or not data.get('zip_code') or not data.get('mobile_number'):
            raise serializers.ValidationError("Street, city, state, zip code, and mobile number are required.")
        # Basic mobile number validation (e.g., 10 digits)
        mobile = data.get('mobile_number')
        if mobile and not mobile.isdigit() or len(mobile) < 10:
            raise serializers.ValidationError({"mobile_number": "Mobile number must be at least 10 digits."})
        return data

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'city', 'state', 'user']
        read_only_fields = ['id', 'user']

class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'mobile', 'city', 'address', 'profile_picture', 'role', 'addresses']
        read_only_fields = ['id', 'username', 'mobile']

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return f"{self.context.get('base_url', 'http://localhost:8000')}{obj.profile_picture.url}"
        return None

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class CustomUserSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(required=False)
    password2 = serializers.CharField(write_only=True, required=False)
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'mobile', 'role', 'first_name', 'last_name', 'city', 'address', 'profile_picture', 'password', 'password2', 'restaurant', 'addresses']
        read_only_fields = ['id']
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    def validate(self, data):
        if 'password' in data and 'password2' in data:
            if data['password'] != data['password2']:
                raise serializers.ValidationError({"password": "Passwords must match"})
        return data

    def create(self, validated_data):
        restaurant_data = validated_data.pop('restaurant', None)
        validated_data.pop('password2', None)
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data.get('password'),
            mobile=validated_data.get('mobile', ''),
            role=validated_data.get('role', 'customer'),
            city=validated_data.get('city', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            address=validated_data.get('address', ''),
            profile_picture=validated_data.get('profile_picture', None)
        )
        if restaurant_data and user.role == 'admin':
            Restaurant.objects.create(user=user, **restaurant_data)
        return user

    def update(self, instance, validated_data):
        restaurant_data = validated_data.pop('restaurant', None)
        validated_data.pop('password', None)
        validated_data.pop('password2', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if restaurant_data and instance.role == 'admin':
            Restaurant.objects.update_or_create(user=instance, defaults=restaurant_data)
        return instance

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user, context={'request': self.context.get('request')}).data
        return data