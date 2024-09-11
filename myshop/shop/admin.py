from django.contrib import admin
from .models import Product
from .models import SpecialOffer

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'origin', 'certification', 'created_at')
    list_filter = ('category', 'origin')
    search_fields = ('name', 'description', 'category')
    
admin.site.register(Product)

@admin.register(SpecialOffer)
class SpecialOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)