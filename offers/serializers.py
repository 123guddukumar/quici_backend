from rest_framework import serializers
from .models import Offer, OfferUsage

class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'

class OfferUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferUsage
        fields = '__all__'