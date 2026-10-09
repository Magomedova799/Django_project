from django import forms
from .models import Comments
from .models import Post

class CommentsForms(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('name', 'email', 'text_comments')

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'description', 'image', 'tags') 
        widgets = {
            'title': forms.TextInput(attrs={'style': 'width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 8px; margin-bottom: 15px;', 'placeholder': 'Заголовок статьи...'}),
            'description': forms.Textarea(attrs={'style': 'width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 8px; margin-bottom: 15px;', 'rows': 6, 'placeholder': 'Текст статьи...'}),
            'image': forms.ClearableFileInput(attrs={'style': 'margin-bottom: 15px;'}),

            'tags': forms.SelectMultiple(attrs={
                'style': 'width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 8px; margin-bottom: 15px; height: 100px;',
            }),
        }

