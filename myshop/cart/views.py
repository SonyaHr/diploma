from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem, Coupon
from django.contrib import messages
from shop.models import Product
from .forms import CouponApplyForm
from django.contrib.auth.decorators import login_required

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('cart:cart_detail')

@login_required
def remove_from_cart(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.delete()
    return redirect('cart:cart_detail')

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    discount = 0
    coupon = None

    if 'coupon_id' in request.session:
        try:
            coupon = Coupon.objects.get(id=request.session['coupon_id'])
            if coupon.is_valid():
                discount = (coupon.discount / 100) * total_price
                total_price -= discount
            else:
                messages.error(request, "The applied coupon is no longer valid.")
                del request.session['coupon_id']
        except Coupon.DoesNotExist:
            messages.error(request, "The applied coupon does not exist.")
            del request.session['coupon_id']

    if request.method == 'POST':
        coupon_form = CouponApplyForm(request.POST)
        if coupon_form.is_valid():
            code = coupon_form.cleaned_data['code']
            try:
                coupon = Coupon.objects.get(code__iexact=code, active=True)
                if not coupon.is_valid():
                    messages.error(request, "This coupon is not valid.")
                else:
                    # Перевірка ліміту використання
                    if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
                        messages.error(request, "This coupon has reached its usage limit.")
                    else:
                        request.session['coupon_id'] = coupon.id
                        discount = (coupon.discount / 100) * total_price
                        total_price -= discount
                        messages.success(request, f"Coupon '{coupon.code}' applied successfully!")
            except Coupon.DoesNotExist:
                messages.error(request, "Invalid coupon code.")
        return redirect('cart:cart_detail')
    else:
        coupon_form = CouponApplyForm()

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'discount': discount,
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
                    request.session['coupon_id'] = coupon.id
                    return redirect('cart:cart_detail')
                else:
                    form.add_error(None, 'This coupon is expired or inactive.')
            except Coupon.DoesNotExist:
                form.add_error(None, 'This coupon does not exist.')

    return redirect('cart:cart_detail')
