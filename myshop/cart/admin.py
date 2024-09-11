from django.contrib import admin
from .models import Coupon
# Register your models here.
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'valid_from', 'valid_to', 'active', 'usage_limit', 'used_count')
    search_fields = ('code',)
    list_filter = ('active', 'valid_from', 'valid_to')
    ordering = ('-valid_from',)