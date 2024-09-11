from django.db import models
from django.conf import settings
from shop.models import Product
from django.utils import timezone
from decimal import Decimal

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey('Coupon', related_name='carts', null=True, blank=True, on_delete=models.SET_NULL)
    shipping_address = models.CharField(max_length=255, blank=True, null=True)  # Пример поля для адреса доставки

    def __str__(self):
        return f"Cart {self.id} for {self.user.username}"

    def total_price(self):
        # Рассчитываем общую стоимость товаров в корзине
        return sum(Decimal(item.total_price()) for item in self.items.all())

    def shipping_cost(self):
        # Логика расчета стоимости доставки
        return Decimal('10.00')

    def discounted_total(self):
        # Общая сумма корзины с учетом скидки, но без доставки
        total_price = Decimal(self.total_price())
        if self.coupon:
            discount_amount = total_price * (Decimal(self.coupon.discount) / Decimal('100'))
            return total_price - discount_amount
        return total_price

    def grand_total(self):
        # Общая сумма с учетом стоимости доставки
        return Decimal(self.discounted_total()) + Decimal(self.shipping_cost())

# Модель товара в корзине
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def product_price(self):
        if self.product.has_discount():
            return Decimal(self.product.discounted_price())
        return Decimal(self.product.price)

    def total_price(self):
        return Decimal(self.quantity) * self.product_price()

    def discounted_price(self):
        total = self.total_price()

        if self.cart.coupon:
            # Если есть купон, применяем дополнительную скидку
            discount = Decimal(self.cart.coupon.discount) / Decimal('100')
            total *= (Decimal('1') - discount)

        return total

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

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    shipping_address = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='Pending')  # Статус заказа

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
