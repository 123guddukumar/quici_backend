from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, RegisterView, CityViewSet, LoginView, UserProfileView, AddressViewSet


router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
# router.register(r'restaurants', RestaurantViewSet)
router.register(r'cities', CityViewSet)
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
]