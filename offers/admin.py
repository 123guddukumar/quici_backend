from django.contrib import admin
from .models import Offer, OfferUsage

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('code', 'offer_type', 'discount_value', 'is_active', 'start_date', 'end_date')
    list_filter = ('offer_type', 'is_active')

@admin.register(OfferUsage)
class OfferUsageAdmin(admin.ModelAdmin):
    list_display = ('offer', 'user', 'used_at')