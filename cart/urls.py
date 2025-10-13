from django.urls import path
from .views import CartView, AddToCartView, CartItemView, cart_cleanup

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('add/', AddToCartView.as_view(), name='add_to_cart'),
    path('items/<int:item_id>/', CartItemView.as_view(), name='cart_item'),
    path('cleanup/', cart_cleanup, name='cart_cleanup'),
]