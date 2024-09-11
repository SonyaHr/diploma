from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem, Coupon, Order, OrderItem
from django.contrib import messages
from shop.models import Product
from .forms import CouponApplyForm, ShippingForm, OrderForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if product.has_discount:
        price = Decimal(product.discount_price)
    else:
        price = Decimal(product.price)

    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.price = price
    cart_item.save()
    
    return redirect('cart:cart_detail')

@login_required
def remove_from_cart(request, cart_item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
    
    cart_item.delete()
    
    return redirect('cart:cart_detail')

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    # Розраховуємо загальну вартість без знижок
    total_price = sum(Decimal(item.total_price()) for item in cart_items)

    # Розраховуємо загальну вартість зі знижками (якщо є купон або індивідуальні знижки на товари)
    discounted_total = sum(Decimal(item.discounted_price()) for item in cart_items)

    # Вираховуємо суму знижки
    discount_amount = total_price - discounted_total

    if request.method == 'POST':
        coupon_form = CouponApplyForm(request.POST)
        if coupon_form.is_valid():
            code = coupon_form.cleaned_data['code']
            try:
                coupon = Coupon.objects.get(code__iexact=code, active=True)
                if not coupon.is_valid():
                    messages.error(request, "This coupon is not valid.")
                else:
                    if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
                        messages.error(request, "This coupon has reached its usage limit.")
                    else:
                        # Застосовуємо купон
                        cart.coupon = coupon
                        cart.save()
                        messages.success(request, f"Coupon '{coupon.code}' applied successfully!")
            except Coupon.DoesNotExist:
                messages.error(request, "Invalid coupon code.")
        return redirect('cart:cart_detail')
    else:
        coupon_form = CouponApplyForm()

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'shipping_cost': Decimal(cart.shipping_cost()),
        'discounted_total': discounted_total,
        'grand_total': discounted_total + Decimal(cart.shipping_cost()),
        'discount_amount': discount_amount,
        'coupon_form': coupon_form,
    }
    return render(request, 'cart/cart_detail.html', context)

@login_required
def apply_coupon(request):
    if request.method == 'POST':
        form = CouponApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                coupon = get_object_or_404(Coupon, code=code)
                
                if coupon.is_valid():
                    cart = get_object_or_404(Cart, user=request.user)
                    cart.coupon = coupon
                    cart.save()
                    messages.success(request, f"Coupon '{coupon.code}' applied successfully!")
                else:
                    form.add_error(None, 'This coupon is expired or inactive.')
            except Coupon.DoesNotExist:
                form.add_error(None, 'This coupon does not exist.')

    return redirect('cart:cart_detail')

@login_required
def update_shipping(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if request.method == 'POST':
        form = ShippingForm(request.POST)
        if form.is_valid():
            cart.shipping_address = form.cleaned_data['address']
            cart.shipping_city = form.cleaned_data['city']
            cart.shipping_zip = form.cleaned_data['zip_code']
            cart.save()
            messages.success(request, "Shipping information updated successfully.")
            return redirect('cart:cart_detail')
        else:
            messages.error(request, "Invalid shipping information.")
    else:
        form = ShippingForm()

    context = {
        'shipping_form': form,
    }
    return render(request, 'cart/cart_detail.html', context)

@login_required
def update_cart_item(request, cart_item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)

    quantity = int(request.POST.get('quantity', 1))  

    cart_item.quantity = quantity
    cart_item.save()

    return redirect('cart:cart_detail')

@login_required
def place_order(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            shipping_address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            zip_code = form.cleaned_data['zip_code']
            total_price = Decimal(cart.total_price())
            shipping_cost = Decimal(cart.shipping_cost())
            grand_total = Decimal(cart.grand_total())

            # Создание заказа
            order = Order.objects.create(
                user=request.user,
                shipping_address=f"{shipping_address}, {city}, {zip_code}",
                total_price=total_price,
                shipping_cost=shipping_cost,
                grand_total=grand_total
            )

            # Добавление товаров в заказ
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=Decimal(item.product_price())
                )

            # Очистка корзины
            cart.items.all().delete()

            messages.success(request, f"Your order #{order.id} has been placed successfully.")
            return render(request, 'cart/order_confirmation.html', {'order': order})
    else:
        form = OrderForm()

    return render(request, 'cart/place_order.html', {'form': form})
