from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from .models import Offer, OfferUsage
from .serializers import OfferSerializer
from orders.models import Order  # To apply offer to order
from django.shortcuts import get_object_or_404

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        if self.request.user.is_staff:
            return Offer.objects.all()
        return Offer.objects.filter(is_active=True, end_date__gte=timezone.now())

class ApplyOfferView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        code = request.data.get('code')
        order_id = request.data.get('order_id')
        offer = get_object_or_404(Offer, code=code, is_active=True, end_date__gte=timezone.now())
        
        # Check usage limits
        total_usages = OfferUsage.objects.filter(offer=offer).count()
        if offer.usage_limit and total_usages >= offer.usage_limit:
            return Response({'error': 'Offer usage limit reached'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_usages = OfferUsage.objects.filter(offer=offer, user=request.user).count()
        if user_usages >= offer.user_usage_limit:
            return Response({'error': 'User usage limit reached for this offer'}, status=status.HTTP_400_BAD_REQUEST)
        
        order = get_object_or_404(Order, id=order_id, user=request.user, status='placed')
        if order.total_amount < offer.min_order_amount:
            return Response({'error': 'Minimum order amount not met'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate discount
        if offer.offer_type == 'percentage':
            discount = (offer.discount_value / 100) * order.total_amount
            if offer.max_discount:
                discount = min(discount, offer.max_discount)
        else:
            discount = offer.discount_value
        
        order.total_amount -= discount
        order.save()
        
        # Record usage
        OfferUsage.objects.create(offer=offer, user=request.user)
        
        return Response({'discount_applied': discount, 'new_total': order.total_amount})