from django.urls import path
from .views import PaymentCreateView, PaymentVerifyView

urlpatterns = [
    path('create/', PaymentCreateView.as_view(), name='payment-create'),
    path('verify/<int:order_id>/', PaymentVerifyView.as_view(), name='payment-verify'),
]