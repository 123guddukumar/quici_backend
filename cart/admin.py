from django.contrib import admin
from .models import Cart, CartItem

# Register your models here.
admin.site.register(Cart)
admin.site.register(CartItem)

# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ('user', 'created_at')

# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = ('cart', 'menu_item', 'quantity')