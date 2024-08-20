from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Comment, UserProfile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    avatar = forms.ImageField(required=False)
    phone = forms.CharField(required=False)
    birthdate = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(required=False)
    city = forms.CharField(required=False)
    country = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'avatar', 'phone', 'birthdate', 'address', 'city', 'country']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile = UserProfile.objects.create(
                user=user,
                avatar=self.cleaned_data.get('avatar'),
                phone=self.cleaned_data.get('phone'),
                birthdate=self.cleaned_data.get('birthdate'),
                address=self.cleaned_data.get('address'),
                city=self.cleaned_data.get('city'),
                country=self.cleaned_data.get('country'),
            )
        return user
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text'] 
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your comment here...'})  # Замінили 'content' на 'text'
        }
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'phone', 'birthdate', 'address', 'city', 'country']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']