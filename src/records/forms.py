from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User
from django import forms

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "first_name", "last_name"]
        # fields = ["username", "email", "password1", "password2", "role"]

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user