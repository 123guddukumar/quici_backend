import razorpay
from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
from orders.models import Order
from django.shortcuts import get_object_or_404

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        order = get_object_or_404(Order, id=self.request.data['order'], user=self.request.user)
        payment = serializer.save(order=order, amount=order.total_amount)
        # Create Razorpay order
        razorpay_order = client.order.create({
            'amount': int(order.total_amount * 100),
            'currency': 'INR',
            'receipt': str(order.id),
        })
        payment.transaction_id = razorpay_order['id']
        payment.save()
        return payment

class PaymentVerifyView(generics.UpdateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Payment, order__id=self.kwargs['order_id'])

    def post(self, request, *args, **kwargs):
        payment = self.get_object()
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': payment.transaction_id,
                'razorpay_payment_id': request.data['razorpay_payment_id'],
                'razorpay_signature': request.data['razorpay_signature']
            })
            payment.status = 'success'
            payment.save()
            payment.order.status = 'accepted'  # Update order status
            payment.order.save()
            return Response({'status': 'success'})
        except:
            payment.status = 'failed'
            payment.save()
            return Response({'status': 'failed'}, status=status.HTTP_400_BAD_REQUEST)