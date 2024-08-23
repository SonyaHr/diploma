from django import forms
from .models import Post, BlogComment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']

class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ['text']

class BlogReplyForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ['text']
