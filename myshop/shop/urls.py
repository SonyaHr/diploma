from django.urls import path

from . import views
from .views import subscribe_newsletter

urlpatterns = [
    path('', views.index, name='index'),  # Головна сторінка
    path('about/', views.about, name='about'),  # Сторінка About
    path('shop/', views.shop, name='shop'),  # Сторінка Shop
    path('quality/', views.quality, name='quality'),  # Сторінка Quality
    path('contact/', views.contact, name='contact'),  # Сторінка Contact
    path('profile/', views.profile_view, name='profile'),  # Сторінка профілю
    path('register/', views.register, name='register'),  # Сторінка реєстрації
    path('login/', views.login_view, name='login'),  # Сторінка входу
    path('logout/', views.logout_view, name='logout'),  # Вихід
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('comment/like/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('comment/dislike/<int:comment_id>/', views.dislike_comment, name='dislike_comment'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('subscribe/', subscribe_newsletter, name='subscribe_newsletter'),
]
