from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from orders.models import Order
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone

class SalesReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        period = request.query_params.get('period', 'daily')
        now = timezone.now()
        if period == 'daily':
            start = now - timedelta(days=1)
        elif period == 'weekly':
            start = now - timedelta(weeks=1)
        elif period == 'monthly':
            start = now - timedelta(days=30)
        else:
            start = now - timedelta(days=1)

        sales = Order.objects.filter(created_at__gte=start, status='delivered').aggregate(total=Sum('total_amount'))
        return Response({'total_sales': sales['total'] or 0})