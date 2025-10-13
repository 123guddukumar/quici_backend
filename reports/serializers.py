# No serializers needed, as reports are custom responses
from rest_framework import serializers

# Placeholder
class ReportSerializer(serializers.Serializer):
    total_sales = serializers.DecimalField(max_digits=10, decimal_places=2)