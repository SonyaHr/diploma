from django import forms
from .models import CartItem

class CartAddProductForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']
        
class CouponApplyForm(forms.Form):
    code = forms.CharField(max_length=50, label='Coupon Code')
    
class ShippingForm(forms.Form):
    address = forms.CharField(widget=forms.Textarea, label='Shipping Address')
    city = forms.CharField(max_length=100, label='City')
    zip_code = forms.CharField(max_length=20, label='ZIP Code')
    
class OrderForm(forms.Form):
    address = forms.CharField(widget=forms.Textarea, label='Shipping Address')
    city = forms.CharField(max_length=100, label='City')
    zip_code = forms.CharField(max_length=20, label='ZIP Code')