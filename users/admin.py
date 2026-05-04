from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import SellerProfile

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'is_verified', 'is_active', 'is_staff', 'created_at')
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff')
    search_fields = ('email', 'phone')
    ordering = ('-created_at',)

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'user', 'is_approved', 'balance')
    list_filter = ('is_approved',)
    search_fields = ('store_name', 'user__email')
