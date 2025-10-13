from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Wishlist, WishlistItem
from .serializers import WishlistSerializer, WishlistItemSerializer
from menu.models import MenuItem
import logging

logger = logging.getLogger(__name__)

class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)
            serializer = WishlistSerializer(wishlist)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching wishlist for user {request.user.username}: {str(e)}")
            return Response({"detail": "Failed to fetch wishlist"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddToWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)
            menu_item_id = request.data.get('menu_item')
            menu_item = MenuItem.objects.get(id=menu_item_id)
            wishlist_item, item_created = WishlistItem.objects.get_or_create(
                wishlist=wishlist,
                menu_item=menu_item
            )
            if not item_created:
                return Response({"detail": "Item already in wishlist"}, status=status.HTTP_400_BAD_REQUEST)
            serializer = WishlistItemSerializer(wishlist_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except MenuItem.DoesNotExist:
            logger.error(f"Menu item {menu_item_id} not found")
            return Response({"detail": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error adding to wishlist for user {request.user.username}: {str(e)}")
            return Response({"detail": "Failed to add to wishlist"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RemoveFromWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            wishlist_item = WishlistItem.objects.get(wishlist__user=request.user, menu_item__id=item_id)
            wishlist_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except WishlistItem.DoesNotExist:
            logger.error(f"Wishlist item {item_id} not found for user {request.user.username}")
            return Response({"detail": "Wishlist item not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting wishlist item {item_id}: {str(e)}")
            return Response({"detail": "Failed to delete wishlist item"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MoveToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):
        try:
            wishlist_item = WishlistItem.objects.get(wishlist__user=request.user, menu_item__id=item_id)
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                menu_item=wishlist_item.menu_item,
                defaults={'quantity': 1}
            )
            if not item_created:
                cart_item.quantity += 1
                cart_item.save()
            wishlist_item.delete() # Remove from wishlist after adding to cart
            return Response({"detail": "Item moved to cart"}, status=status.HTTP_200_OK)
        except WishlistItem.DoesNotExist:
            logger.error(f"Wishlist item {item_id} not found for user {request.user.username}")
            return Response({"detail": "Wishlist item not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error moving wishlist item {item_id} to cart: {str(e)}")
            return Response({"detail": "Failed to move to cart"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)