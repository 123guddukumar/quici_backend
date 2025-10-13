from django.urls import path
from .views import WishlistView, AddToWishlistView, RemoveFromWishlistView, MoveToCartView

urlpatterns = [
    path('', WishlistView.as_view(), name='wishlist'),
    path('add/', AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('remove/<int:item_id>/', RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
    path('move-to-cart/<int:item_id>/', MoveToCartView.as_view(), name='move_to_cart'),
]