from django.urls import path, include
from rest_framework.routers import DefaultRouter
from menu.views import MenuViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'items', MenuViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]