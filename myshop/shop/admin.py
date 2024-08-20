from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'origin', 'certification', 'created_at')
    list_filter = ('category', 'origin')
    search_fields = ('name', 'description', 'category')
    
admin.site.register(Product)