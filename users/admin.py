from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import City
from .models import Address

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'mobile', 'role', 'created_at')
    list_filter = ('role',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('mobile', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('mobile', 'role')}),
    )

admin.site.register(City)
admin.site.register(Address)