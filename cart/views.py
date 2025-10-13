from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from cart.serializers import CartSerializer, CartItemSerializer
from menu.models import MenuItem
import logging

logger = logging.getLogger(__name__)

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching cart for user {request.user.username}: {str(e)}")
            return Response({"detail": "Failed to fetch cart"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            menu_item_id = request.data.get('menu_item')
            quantity = int(request.data.get('quantity', 1))
            
            if quantity < 1:
                return Response({"detail": "Quantity must be at least 1"}, status=status.HTTP_400_BAD_REQUEST)

            menu_item = MenuItem.objects.get(id=menu_item_id)
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                menu_item=menu_item,
                defaults={'quantity': quantity}
            )
            if not item_created:
                cart_item.quantity += quantity
                cart_item.save()
            
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except MenuItem.DoesNotExist:
            logger.error(f"Menu item {menu_item_id} not found")
            return Response({"detail": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error adding to cart for user {request.user.username}: {str(e)}")
            return Response({"detail": "Failed to add to cart"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(cart__user=request.user, menu_item__id=item_id)
            quantity = int(request.data.get('quantity'))
            if quantity < 1:
                cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            cart_item.quantity = quantity
            cart_item.save()
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            logger.error(f"Cart item {item_id} not found for user {request.user.username}")
            return Response({"detail": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating cart item {item_id}: {str(e)}")
            return Response({"detail": "Failed to update cart item"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(cart__user=request.user, menu_item__id=item_id)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            logger.error(f"Cart item {item_id} not found for user {request.user.username}")
            return Response({"detail": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting cart item {item_id}: {str(e)}")
            return Response({"detail": "Failed to delete cart item"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Cart
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def cart_cleanup(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()
        cart.delete()
        logger.info(f"Cart and items cleaned up for user {request.user.username}")
        return Response({"detail": "Cart cleared successfully"}, status=status.HTTP_200_OK)
    except Cart.DoesNotExist:
        logger.info(f"No cart to clean up for user {request.user.username}")
        return Response({"detail": "No cart to clear"}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error during cart cleanup for user {request.user.username}: {str(e)}")
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)