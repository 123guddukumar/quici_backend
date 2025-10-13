# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import api_view, permission_classes
# from django.views.decorators.csrf import csrf_exempt
# from .models import Order
# from .serializers import OrderSerializer
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
# import logging
# import razorpay
# from django.conf import settings
# from django.db.utils import ProgrammingError

# logger = logging.getLogger(__name__)

# razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# class OrderView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         try:
#             if request.user.role == 'admin':
#                 orders = Order.objects.all().order_by('-created_at')
#             else:
#                 orders = Order.objects.filter(user=request.user).order_by('-created_at')
#             serializer = OrderSerializer(orders, many=True)
#             return Response(serializer.data)
#         except Exception as e:
#             logger.error(f"Error fetching orders: {str(e)}")
#             return Response({"detail": "Failed to fetch orders"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def post(self, request):
#         try:
#             serializer = OrderSerializer(data=request.data, context={'request': request})
#             if serializer.is_valid():
#                 order = serializer.save()
#                 # Send WebSocket notification
#                 channel_layer = get_channel_layer()
#                 async_to_sync(channel_layer.group_send)(
#                     f'user_{request.user.id}',
#                     {
#                         'type': 'order_notification',
#                         'order': OrderSerializer(order).data,
#                     }
#                 )
#                 async_to_sync(channel_layer.group_send)(
#                     'user_admin',
#                     {
#                         'type': 'order_notification',
#                         'order': OrderSerializer(order).data,
#                     }
#                 )
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             logger.error(f"Serializer validation failed: {serializer.errors}")
#             return Response(
#                 {
#                     "detail": "Invalid order data",
#                     "errors": serializer.errors
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         except ProgrammingError as e:
#             error_msg = str(e)
#             logger.error(f"Database error creating order: {error_msg}")
#             if 'no column named price' in error_msg:
#                 return Response(
#                     {
#                         "detail": "Database schema error: table orders_orderitem has no column named price. "
#                              "Run 'python manage.py makemigrations orders' and 'python manage.py migrate' to fix."
#                     },
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                 )
#             if 'NOT NULL constraint failed: orders_orderitem.price' in error_msg:
#                 return Response(
#                     {
#                         "detail": "Database error: orders_orderitem.price cannot be null. "
#                              "Ensure OrderItemSerializer sets price from menu_item.price."
#                     },
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                 )
#             return Response({"detail": f"Database error: {error_msg}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             logger.error(f"Error creating order: {str(e)}")
#             return Response({"detail": f"Failed to create order: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class OrderDetailView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get_object(self, pk):
#         try:
#             if self.request.user.role == 'admin':
#                 return Order.objects.get(pk=pk)
#             return Order.objects.get(pk=pk, user=self.request.user)
#         except Order.DoesNotExist:
#             return None

#     def get(self, request, pk):
#         order = self.get_object(pk)
#         if not order:
#             return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
#         serializer = OrderSerializer(order)
#         return Response(serializer.data)

#     def patch(self, request, pk):
#         try:
#             order = self.get_object(pk)
#             if not order:
#                 return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
#             serializer = OrderSerializer(order, data=request.data, partial=True, context={'request': request})
#             if serializer.is_valid():
#                 order = serializer.save()
#                 channel_layer = get_channel_layer()
#                 async_to_sync(channel_layer.group_send)(
#                     f'user_{order.user.id}',
#                     {
#                         'type': 'order_notification',
#                         'order': OrderSerializer(order).data,
#                     }
#                 )
#                 async_to_sync(channel_layer.group_send)(
#                     'user_admin',
#                     {
#                         'type': 'order_notification',
#                         'order': OrderSerializer(order).data,
#                     }
#                 )
#                 return Response(serializer.data)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             logger.error(f"Error updating order {pk}: {str(e)}")
#             return Response({"detail": "Failed to update order"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status
# import razorpay
# from .models import Order
# from django.conf import settings

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_razorpay_order(request):
#     try:
#         order_id = request.data.get('order_id')
#         order = Order.objects.get(id=order_id, user=request.user)

#         if order.payment_method != 'razorpay':
#             return Response({"detail": "Order payment method is not Razorpay"}, status=status.HTTP_400_BAD_REQUEST)

#         client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#         razorpay_order = client.order.create({
#             'amount': int(float(order.total_amount) * 100),  # paise
#             'currency': 'INR',
#             'payment_capture': 1,
#         })

#         return Response({
#             'id': razorpay_order['id'],  
#             'amount': razorpay_order['amount'],
#             'currency': razorpay_order['currency']
#         }, status=status.HTTP_201_CREATED)

#     except Order.DoesNotExist:
#         return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def verify_razorpay_payment(request):
#     try:
#         razorpay_order_id = request.data.get('razorpay_order_id')
#         razorpay_payment_id = request.data.get('razorpay_payment_id')
#         razorpay_signature = request.data.get('razorpay_signature')
#         order_id = request.data.get('order_id')

#         client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#         client.utility.verify_payment_signature({
#             'razorpay_order_id': razorpay_order_id,
#             'razorpay_payment_id': razorpay_payment_id,
#             'razorpay_signature': razorpay_signature,
#         })

#         # Payment successful → ab order confirm
#         order = Order.objects.get(id=order_id, user=request.user)
#         order.payment_status = 'paid'
#         order.status = 'confirmed'
#         order.save()

#         return Response({"detail": "Payment verified successfully", "order_id": order_id}, status=status.HTTP_200_OK)

#     except Order.DoesNotExist:
#         return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
#     except razorpay.errors.SignatureVerificationError:
#         return Response({"detail": "Payment signature verification failed"}, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from .models import Order
from .serializers import OrderSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging
import razorpay
from django.conf import settings
from django.db.utils import ProgrammingError
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from django.utils import timezone
from users.models import Restaurant

logger = logging.getLogger(__name__)

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            period = request.query_params.get('period', None)
            user_id = request.query_params.get('user')
            logger.debug(f"Fetching orders for user_id: {user_id or request.user.id}, period: {period}, requester: {request.user.username} (role: {request.user.role})")

            if user_id and request.user.role == 'admin':
                try:
                    restaurant = Restaurant.objects.get(user__id=user_id)
                    logger.debug(f"Found restaurant for user_id {user_id}: {restaurant.name} (ID: {restaurant.id})")
                    orders = Order.objects.filter(restaurant=restaurant)
                except Restaurant.DoesNotExist:
                    logger.error(f"No restaurant found for user_id: {user_id}")
                    return Response({"detail": "Restaurant not found for this admin"}, status=status.HTTP_404_NOT_FOUND)
            else:
                if request.user.role == 'admin':
                    try:
                        restaurant = Restaurant.objects.get(user=request.user)
                        logger.debug(f"Admin fetching orders for restaurant: {restaurant.name} (ID: {restaurant.id})")
                        orders = Order.objects.filter(restaurant=restaurant)
                    except Restaurant.DoesNotExist:
                        logger.error(f"No restaurant found for admin: {request.user.username}")
                        return Response({"detail": "Restaurant not found for this admin"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    orders = Order.objects.filter(user=request.user)
                    logger.debug(f"Fetching orders for non-admin user: {request.user.username}")

            if period:
                now = timezone.now()
                start_date = None
                if period == 'today':
                    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                elif period == '1week':
                    start_date = now - timedelta(days=7)
                elif period == '7weeks':
                    start_date = now - timedelta(weeks=7)
                elif period == '1month':
                    start_date = now - timedelta(days=30)
                elif period == '3months':
                    start_date = now - timedelta(days=90)
                elif period == '6months':
                    start_date = now - timedelta(days=180)
                elif period == '1year':
                    start_date = now - timedelta(days=365)
                else:
                    logger.warning(f"Invalid period: {period}")
                    return Response({"detail": f"Invalid period: {period}"}, status=status.HTTP_400_BAD_REQUEST)
                if start_date:
                    orders = orders.filter(created_at__gte=start_date)
                    logger.debug(f"Filtered orders by period {period}: start_date={start_date}, count={orders.count()}")

            orders = orders.order_by('-created_at')
            logger.debug(f"Order queryset: {list(orders.values('id', 'order_number', 'status', 'total_amount', 'restaurant__id', 'created_at'))}")
            serializer = OrderSerializer(orders, many=True)
            logger.debug(f"Serialized orders: {len(serializer.data)} orders")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching orders: {str(e)}", exc_info=True)
            return Response({"detail": "Failed to fetch orders"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.debug(f"Order creation request from user: {request.user.username} (role: {request.user.role}), payload: {request.data}, items: {request.data.get('items', [])}")
            serializer = OrderSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                order = serializer.save()
                logger.info(f"Order #{order.order_number} created for restaurant: {order.restaurant.name if order.restaurant else 'None'}")
                channel_layer = get_channel_layer()
                try:
                    items_summary = ", ".join([f"{item['menu_item_name']} (₹{item['price']} x {item['quantity']})" for item in serializer.data['items']])
                    customer_message = f"Order placed: {items_summary}, Total: ₹{order.total_amount:.2f}"
                    admin_message = f"New order received: {items_summary}, Total: ₹{order.total_amount:.2f}"
                    
                    # Customer notification
                    async_to_sync(channel_layer.group_send)(
                        f'user_{request.user.id}',
                        {
                            'type': 'order_notification',
                            'order_id': order.id,
                            'message': customer_message,
                            'items': serializer.data['items'],
                            'total_amount': float(order.total_amount)
                        }
                    )
                    # Admin notification (only for new orders)
                    async_to_sync(channel_layer.group_send)(
                        'user_admin',
                        {
                            'type': 'order_notification',
                            'order_id': order.id,
                            'message': admin_message,
                            'items': serializer.data['items'],
                            'total_amount': float(order.total_amount)
                        }
                    )
                    logger.debug(f"Sent WebSocket notifications for order #{order.order_number}")
                except Exception as ws_error:
                    logger.error(f"WebSocket notification failed for order #{order.order_number}: {str(ws_error)}", exc_info=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            logger.error(f"Serializer validation failed: {serializer.errors}")
            return Response(
                {
                    "detail": "Invalid order data",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except ProgrammingError as e:
            error_msg = str(e)
            logger.error(f"Database error creating order: {error_msg}", exc_info=True)
            if 'no column named price' in error_msg:
                return Response(
                    {
                        "detail": "Database schema error: table orders_orderitem has no column named price. "
                                 "Run 'python manage.py makemigrations orders' and 'python manage.py migrate' to fix."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            if 'NOT NULL constraint failed: orders_orderitem.price' in error_msg:
                return Response(
                    {
                        "detail": "Database error: orders_orderitem.price cannot be null. "
                                 "Ensure OrderItemSerializer sets price from menu_item.price."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return Response({"detail": f"Database error: {error_msg}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}", exc_info=True)
            return Response({"detail": f"Failed to create order: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            if self.request.user.role == 'admin':
                restaurant = Restaurant.objects.get(user=self.request.user)
                logger.debug(f"Fetching order {pk} for admin restaurant: {restaurant.name} (ID: {restaurant.id})")
                return Order.objects.get(pk=pk, restaurant=restaurant)
            logger.debug(f"Fetching order {pk} for non-admin user: {self.request.user.username}")
            return Order.objects.get(pk=pk, user=self.request.user)
        except Order.DoesNotExist:
            logger.error(f"Order {pk} not found")
            return None

    def get(self, request, pk):
        order = self.get_object(pk)
        if not order:
            return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            order = self.get_object(pk)
            if not order:
                return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
            logger.debug(f"Updating order {pk} with data: {request.data}")
            serializer = OrderSerializer(order, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                order = serializer.save()
                channel_layer = get_channel_layer()
                try:
                    items_summary = ", ".join([f"{item['menu_item_name']} (₹{item['price']} x {item['quantity']})" for item in serializer.data['items']])
                    status_messages = {
                        'pending': f"Order pending: {items_summary}, Total: ₹{order.total_amount:.2f}",
                        'confirmed': f"Order confirmed: {items_summary}, Total: ₹{order.total_amount:.2f}",
                        'preparing': f"Order being prepared: {items_summary}, Total: ₹{order.total_amount:.2f}",
                        'out_for_delivery': f"Order out for delivery: {items_summary}, Total: ₹{order.total_amount:.2f}",
                        'delivered': f"Order delivered: {items_summary}, Total: ₹{order.total_amount:.2f}",
                        'cancelled': f"Order cancelled: {items_summary}, Total: ₹{order.total_amount:.2f}",
                    }
                    message = status_messages.get(order.status, f"Order status updated: {items_summary}, Total: ₹{order.total_amount:.2f}")
                    # Customer notification (all status updates)
                    async_to_sync(channel_layer.group_send)(
                        f'user_{order.user.id}',
                        {
                            'type': 'order_notification',
                            'order_id': order.id,
                            'message': message,
                            'items': serializer.data['items'],
                            'total_amount': float(order.total_amount)
                        }
                    )
                    # Admin notification (skip for non-pending statuses)
                    logger.debug(f"Order #{order.order_number} updated to {order.status}")
                except Exception as ws_error:
                    logger.error(f"WebSocket notification failed for order #{order.order_number}: {str(ws_error)}", exc_info=True)
                return Response(serializer.data)
            logger.error(f"Serializer validation failed for order {pk}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating order {pk}: {str(e)}", exc_info=True)
            return Response({"detail": "Failed to update order"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_id = request.query_params.get('user')
            logger.debug(f"Fetching stats for user_id: {user_id or request.user.id}, requester: {request.user.username} (role: {request.user.role})")
            
            if request.user.role != 'admin':
                return Response({"detail": "Only admins can access stats"}, status=status.HTTP_403_FORBIDDEN)

            if user_id:
                try:
                    restaurant = Restaurant.objects.get(user__id=user_id)
                    logger.debug(f"Found restaurant for user_id {user_id}: {restaurant.name} (ID: {restaurant.id})")
                except Restaurant.DoesNotExist:
                    logger.error(f"No restaurant found for user_id: {user_id}")
                    return Response({"detail": "Restaurant not found for this admin"}, status=status.HTTP_404_NOT_FOUND)
            else:
                restaurant = Restaurant.objects.get(user=request.user)
                logger.debug(f"Using default restaurant for user {request.user.username}: {restaurant.name} (ID: {restaurant.id})")

            orders = Order.objects.filter(restaurant=restaurant)
            total_items = orders.aggregate(total_items=Sum('items__quantity'))['total_items'] or 0
            total_orders = orders.count()
            total_revenue = orders.filter(status='delivered').aggregate(total_revenue=Sum('total_amount'))['total_revenue'] or 0
            today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            todays_orders = orders.filter(created_at__gte=today).count()

            logger.debug(f"Stats for user_id {user_id or request.user.id}: {total_items=}, {total_orders=}, {total_revenue=}, {todays_orders=}")
            return Response({
                'total_items': total_items,
                'total_orders': total_orders,
                'total_revenue': float(total_revenue),
                'todays_orders': todays_orders,
            })
        except Restaurant.DoesNotExist:
            logger.error(f"Restaurant not found for admin user {request.user.username}")
            return Response({"detail": "Restaurant not found for this admin"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching order stats: {str(e)}", exc_info=True)
            return Response({"detail": "Failed to fetch order stats"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_razorpay_order(request):
    try:
        amount = request.data.get('amount')
        logger.debug(f"Creating Razorpay order with amount: {amount}")
        if not amount or not isinstance(amount, (int, float)) or amount <= 0:
            logger.error(f"Invalid amount: {amount}")
            return Response({"detail": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
        razorpay_order = razorpay_client.order.create({
            'amount': int(amount),
            'currency': 'INR',
            'payment_capture': 1,
        })
        logger.info(f"Created Razorpay order: {razorpay_order['id']}")
        return Response({
            'id': razorpay_order['id'],
            'amount': razorpay_order['amount'],
            'currency': razorpay_order['currency']
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error creating Razorpay order: {str(e)}", exc_info=True)
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_razorpay_payment(request):
    try:
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')
        order_id = request.data.get('order_id')
        logger.debug(f"Verifying payment for order_id: {order_id}, razorpay_order_id: {razorpay_order_id}")
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
        order = Order.objects.get(id=order_id, user=request.user)
        order.payment_status = 'paid'
        order.status = 'confirmed'
        order.save()
        logger.info(f"Payment verified for order {order_id}")
        channel_layer = get_channel_layer()
        try:
            items_summary = ", ".join([f"{item['menu_item_name']} (₹{item['price']} x {item['quantity']})" for item in OrderSerializer(order).data['items']])
            # Customer notification for payment confirmation
            async_to_sync(channel_layer.group_send)(
                f'user_{request.user.id}',
                {
                    'type': 'order_notification',
                    'order_id': order.id,
                    'message': f"Payment confirmed: {items_summary}, Total: ₹{order.total_amount:.2f}",
                    'items': OrderSerializer(order).data['items'],
                    'total_amount': float(order.total_amount)
                }
            )
            logger.debug(f"Sent WebSocket notification for payment confirmation of order #{order.order_number}")
        except Exception as ws_error:
            logger.error(f"WebSocket notification failed for payment confirmation of order #{order.order_number}: {str(ws_error)}", exc_info=True)
        return Response({"detail": "Payment verified successfully", "order_id": order_id}, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    except razorpay.errors.SignatureVerificationError:
        logger.error("Payment signature verification failed")
        return Response({"detail": "Payment signature verification failed"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}", exc_info=True)
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)