from rest_framework import permissions
from users.models import CustomUser, Restaurant

class IsRestaurantAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == 'admin':
            try:
                restaurant = Restaurant.objects.get(user=request.user)
                return obj.restaurant == restaurant
            except Restaurant.DoesNotExist:
                return False
        return False