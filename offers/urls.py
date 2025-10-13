from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferViewSet, ApplyOfferView

router = DefaultRouter()
router.register(r'offers', OfferViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('apply/', ApplyOfferView.as_view(), name='apply-offer'),
]