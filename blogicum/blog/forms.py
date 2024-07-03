from django import forms
from django.contrib.auth import get_user_model

from .models import Post, Comment


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)

        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
