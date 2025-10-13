from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import MenuItem, Category, Rating
from .serializers import MenuItemSerializer, MenuItemCreateSerializer, CategorySerializer, RatingSerializer
import logging

logger = logging.getLogger(__name__)

class MenuViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MenuItemCreateSerializer
        return MenuItemSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'admin':
            try:
                restaurant = user.restaurant
                return MenuItem.objects.filter(restaurant=restaurant)
            except AttributeError:
                logger.error(f"User {user.username} with role 'admin' has no associated restaurant")
                return MenuItem.objects.none()
        return MenuItem.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'admin':
            logger.error(f"User {user.username} attempted to create menu item without admin role")
            return Response({"detail": "Only restaurant admins can add menu items."}, status=status.HTTP_403_FORBIDDEN)
        try:
            restaurant = user.restaurant
            serializer.save(restaurant=restaurant)
            logger.info(f"Menu item created by {user.username} for restaurant {restaurant.name}")
        except AttributeError:
            logger.error(f"User {user.username} has no associated restaurant")
            return Response({"detail": "No restaurant associated with this user."}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        user = self.request.user
        if user.role != 'admin':
            logger.error(f"User {user.username} attempted to update menu item without admin role")
            return Response({"detail": "Only restaurant admins can update menu items."}, status=status.HTTP_403_FORBIDDEN)
        try:
            restaurant = user.restaurant
            serializer.save(restaurant=restaurant)
            logger.info(f"Menu item updated by {user.username} for restaurant {restaurant.name}")
        except AttributeError:
            logger.error(f"User {user.username} has no associated restaurant")
            return Response({"detail": "No restaurant associated with this user."}, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role != 'admin':
            logger.error(f"User {user.username} attempted to delete menu item without admin role")
            return Response({"detail": "Only restaurant admins can delete menu items."}, status=status.HTTP_403_FORBIDDEN)
        logger.info(f"Menu item {instance.name} deleted by {user.username}")
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rate(self, request, pk=None):
        menu_item = self.get_object()
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            rating_value = serializer.validated_data['rating']
            review = serializer.validated_data.get('review', '')
            if not 1 <= rating_value <= 5:
                return Response({"detail": "Rating must be between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)
            Rating.objects.update_or_create(
                user=request.user,
                menu_item=menu_item,
                defaults={'rating': rating_value, 'review': review}
            )
            logger.info(f"Rating submitted for menu item {menu_item.name} by {request.user.username}")
            return Response({"detail": "Rating and review submitted successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]