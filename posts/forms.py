from django import forms
from .models import Post, Comment
from django_ckeditor_5.widgets import CKEditor5Widget

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content',)

        widgets = {
            'title': forms.TextInput(attrs={'class': 'input', 'type': 'text', 'placeholder': 'Titel'}),
            'content': CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5"}, config_name="extends"
              )
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

        widgets = {
            'content': forms.TextInput(attrs={'class': 'input', 'type': 'text', 'placeholder': 'Kommentar'}),
        }