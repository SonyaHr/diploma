
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.safestring import mark_safe

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('honey', 'Honey'),
        ('beeswax', 'Beeswax'),
        ('pollen', 'Pollen'),
        ('propolis', 'Propolis'),
    ]
    
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='honey')
    volume = models.CharField(max_length=50, blank=True, null=True)  
    origin = models.CharField(max_length=100, blank=True, null=True) 
    certification = models.CharField(max_length=100, blank=True, null=True) 

    def __str__(self):
        return self.name

class Comment(models.Model):
    product = models.ForeignKey(Product, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.product.name}"
    
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class CommentVote(models.Model):
    VOTE_TYPE = (
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name='votes', on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=7, choices=VOTE_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment', 'vote_type')