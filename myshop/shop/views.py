from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Comment, CommentVote, NewsletterSubscription
from cart.models import Cart, CartItem
from cart.forms import CartAddProductForm 
from .forms import UserRegisterForm, CommentForm, UserProfileForm, UserUpdateForm, NewsletterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages

# Головна сторінка
def index(request):
    now = timezone.now()
    featured_products = Product.objects.filter(
        discount_price__isnull=False,
        discount_start_date__lte=now,
        discount_end_date__gte=now
    )[:3] 

    return render(request, 'shop/index.html', {
        'featured_products': featured_products,
    })
# Сторінка магазину
def shop(request):
    category_filter = request.GET.get('category', None)
    search_query = request.GET.get('search', '')
    products = Product.objects.all()
    if category_filter:
        products = products.filter(category=category_filter)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'shop/shop.html', {
        'products': page_obj,
        'category_choices': Product.CATEGORY_CHOICES,
        'selected_category': category_filter,
    })

# Додавання товару в кошик
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cart_item, _ = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity += form.cleaned_data['quantity']
        cart_item.save()
    
    return redirect('cart_detail')

# Перегляд кошика
@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all() 
    total_price = cart.total_price()
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart': cart,
    }
    return render(request, 'shop/cart_detail.html', context)

# Видалення товару з кошика
@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('cart_detail')

# Реєстрація користувача
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
    else:
        form = UserRegisterForm()
    return render(request, 'shop/register.html', {'form': form})

# Логін користувача
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

# Вихід користувача
def logout_view(request):
    logout(request)
    return redirect('index')

# Додаткові сторінки
def about(request):
    return render(request, 'shop/about.html')

def quality(request):
    return render(request, 'shop/quality.html')

def contact(request):
    return render(request, 'shop/contact.html')

# Сторінка профілю користувача
@login_required
def profile_view(request):
    return render(request, 'shop/profile.html')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    comments = product.comments.all() 
    if request.method == 'POST':
        if request.user.is_authenticated:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.product = product
                comment.user = request.user
                comment.save()
                return redirect('product_detail', product_id=product.id)
        else:
            return redirect('login')
    else:
        comment_form = CommentForm()

    # Пагінація
    paginator = Paginator(comments, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'page_obj': page_obj,
        'comment_form': comment_form,
    })

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    existing_vote = CommentVote.objects.filter(user=request.user, comment=comment).first()
    if existing_vote:
        if existing_vote.vote_type == 'like':
            return JsonResponse({'error': 'Вы уже проголосовали.'})  
        elif existing_vote.vote_type == 'dislike':
            existing_vote.delete()
            CommentVote.objects.create(user=request.user, comment=comment, vote_type='like')
    else:
        CommentVote.objects.create(user=request.user, comment=comment, vote_type='like')

    comment.likes = CommentVote.objects.filter(comment=comment, vote_type='like').count()
    comment.dislikes = CommentVote.objects.filter(comment=comment, vote_type='dislike').count()
    comment.save()

    return JsonResponse({
        'likes': comment.likes,
        'dislikes': comment.dislikes
    }) 

@login_required
def dislike_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    existing_vote = CommentVote.objects.filter(user=request.user, comment=comment).first()
    if existing_vote:
        if existing_vote.vote_type == 'dislike':
            return JsonResponse({'error': 'Вы уже проголосовали.'})  
        elif existing_vote.vote_type == 'like':
            existing_vote.delete()
            CommentVote.objects.create(user=request.user, comment=comment, vote_type='dislike')
    else:
        CommentVote.objects.create(user=request.user, comment=comment, vote_type='dislike')

    comment.likes = CommentVote.objects.filter(comment=comment, vote_type='like').count()
    comment.dislikes = CommentVote.objects.filter(comment=comment, vote_type='dislike').count()
    comment.save()

    return JsonResponse({
        'likes': comment.likes,
        'dislikes': comment.dislikes
    })  

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)
    
    return render(request, 'shop/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
    
def subscribe_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if NewsletterSubscription.objects.filter(email=email).exists():
                messages.error(request, 'This email is already subscribed.')
            else:
                form.save()
                messages.success(request, 'You have been successfully subscribed to the newsletter.')
            return redirect('index') 
    else:
        form = NewsletterForm()
    return render(request, 'shop/newsletter_form.html', {'form': form})

