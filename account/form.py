from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'example@mail.com'})
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Имя'
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Фамилия'
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name') 

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Пользователь с таким email уже зарегистрирован'
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'specialization',
            'portfolio_url',
            'bio',
            'avatar'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'style': 'width: 100%; padding: 8px; border: 1px solid #dbdbdb; border-radius: 4px; margin-bottom: 10px;',
                'placeholder': 'Имя'
            }),
            'last_name': forms.TextInput(attrs={
                'style': 'width: 100%; padding: 8px; border: 1px solid #dbdbdb; border-radius: 4px; margin-bottom: 10px;',
                'placeholder': 'Фамилия'
            }),
            'specialization': forms.TextInput(attrs={
                'style': 'width: 100%; padding: 8px; border: 1px solid #dbdbdb; border-radius: 4px; margin-bottom: 10px;',
                'placeholder': 'Специализация'
            }),
            'portfolio_url': forms.URLInput(attrs={
                'style': 'width: 100%; padding: 8px; border: 1px solid #dbdbdb; border-radius: 4px; margin-bottom: 10px;',
                'placeholder': 'https://example.com'
            }),
            'bio': forms.Textarea(attrs={
                'style': 'width: 100%; padding: 8px; border: 1px solid #dbdbdb; border-radius: 4px; margin-bottom: 10px;',
                'rows': 4,
                'placeholder': 'О себе'
            }),
            'avatar': forms.ClearableFileInput(attrs={
                'style': 'margin-bottom: 10px;'
            }),
        } 
