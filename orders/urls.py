from django.urls import path
from .views import OrderView, OrderDetailView, create_razorpay_order, verify_razorpay_payment,OrderStatsView

urlpatterns = [
    path('', OrderView.as_view(), name='order-list-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('razorpay/order/', create_razorpay_order, name='create-razorpay-order'),
    path('razorpay/verify/', verify_razorpay_payment, name='verify-razorpay-payment'),
    path('stats/', OrderStatsView.as_view(), name='order-stats'),
]