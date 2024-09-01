from django import forms
from .models import CartItem

class CartAddProductForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']
        
class CouponApplyForm(forms.Form):
    code = forms.CharField(max_length=50, label='Coupon Code')