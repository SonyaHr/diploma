
from django.db import models
from django.conf import settings
from shop.models import Product  
from django.utils import timezone

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey('Coupon', related_name='carts', null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self):
        return f"Cart {self.id} for {self.user.username}"

    def total_price(self):
        total = sum(item.total_price() for item in self.items.all())
        if self.coupon:
            total -= total * (self.coupon.discount / 100)
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def total_price(self):
        return self.quantity * self.product.price

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.PositiveIntegerField(help_text="Percentage discount (e.g., 10 for 10%)")
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Number of times this coupon can be used")
    used_count = models.PositiveIntegerField(default=0, help_text="Number of times this coupon has been used")

    def is_valid(self):
        now = timezone.now()
        if self.active and self.valid_from <= now <= self.valid_to:
            if self.usage_limit is None or self.used_count < self.usage_limit:
                return True
        return False

    def __str__(self):
        return self.code