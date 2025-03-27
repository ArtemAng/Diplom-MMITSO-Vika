from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User, Document, DocumentType
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

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'issue_date', 'expiry_date', 'file_path']
        labels = {
            'document_type': 'Тип документа',
            'issue_date': 'Дата выдачи',
            'expiry_date': 'Срок действия',
            'file_path': 'Файл документа'
        }
        widgets = {
            'issue_date': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'placeholder': 'дд/мм/гггг'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'placeholder': 'дд/мм/гггг'
            }),
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'file_path': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_issue_date(self):
        date = self.cleaned_data['issue_date']
        print(f"Получена дата: {date}, тип: {type(date)}")  # Отладочный вывод
        if isinstance(date, str):
            try:
                # Преобразуем дату из формата DD/MM/YYYY в YYYY-MM-DD
                day, month, year = date.split('/')
                date = f"{year}-{month}-{day}"
                print(f"Преобразованная дата: {date}")  # Отладочный вывод
            except ValueError:
                raise forms.ValidationError("Введите корректную дату в формате дд/мм/гггг")
        return date

    def clean_expiry_date(self):
        date = self.cleaned_data['expiry_date']
        print(f"Получена дата: {date}, тип: {type(date)}")  # Отладочный вывод
        if date and isinstance(date, str):
            try:
                # Преобразуем дату из формата DD/MM/YYYY в YYYY-MM-DD
                day, month, year = date.split('/')
                date = f"{year}-{month}-{day}"
                print(f"Преобразованная дата: {date}")  # Отладочный вывод
            except ValueError:
                raise forms.ValidationError("Введите корректную дату в формате дд/мм/гггг")
        return date 