from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User, Document, DocumentType
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re
from django.utils.translation import gettext_lazy as _

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

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
        fields = ['document_type', 'issue_date', 'expiry_date', 'file_path', 'original_filename']
        labels = {
            'document_type': 'Тип документа',
            'issue_date': 'Дата выдачи',
            'expiry_date': 'Срок действия',
            'file_path': 'Файл документа',
            'original_filename': 'Название документа'
        }
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'file_path': forms.FileInput(attrs={'class': 'form-control'}),
            'original_filename': forms.TextInput(attrs={'class': 'form-control'})
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

    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get('issue_date')
        expiry_date = cleaned_data.get('expiry_date')
        
        # Проверка, что дата окончания не меньше даты выдачи
        if issue_date and expiry_date and expiry_date < issue_date:
            raise forms.ValidationError("Дата окончания документа не может быть меньше даты выдачи.")
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if 'file_path' in self.files:
            file = self.files['file_path']
            instance.original_filename = file.name
        if commit:
            instance.save()
        return instance

class SignupForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': ' '}),
        required=True
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
        required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
        required=True
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': ' '}),
        help_text='Пароль должен содержать минимум 8 символов, включая заглавные и строчные буквы, цифры и специальные символы.',
        required=True
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': ' '}),
        help_text='Повторите пароль для подтверждения.',
        required=True
    )
    agree_policy = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input me-2'}),
        label='Я согласен на обработку персональных данных',
        help_text='Для регистрации необходимо согласиться с условиями <a href="/privacy-policy/" target="_blank">пользовательского соглашения</a>.'
    )

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            # Проверка минимальной длины
            if len(password) < 8:
                raise ValidationError('Пароль должен содержать минимум 8 символов.')
            
            # Проверка наличия заглавных букв
            if not re.search(r'[A-Z]', password):
                raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву.')
            
            # Проверка наличия строчных букв
            if not re.search(r'[a-z]', password):
                raise ValidationError('Пароль должен содержать хотя бы одну строчную букву.')
            
            # Проверка наличия цифр
            if not re.search(r'\d', password):
                raise ValidationError('Пароль должен содержать хотя бы одну цифру.')
            
            # Проверка наличия специальных символов
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValidationError('Пароль должен содержать хотя бы один специальный символ (!@#$%^&*(),.?":{}|<>).')
            
            # Проверка на общие пароли
            common_passwords = ['password', '12345678', 'qwerty123', 'admin123']
            if password.lower() in common_passwords:
                raise ValidationError('Этот пароль слишком простой. Пожалуйста, выберите другой пароль.')
            
            # Используем встроенную валидацию Django
            try:
                validate_password(password)
            except ValidationError as e:
                raise ValidationError(e.messages)
        
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Пароли не совпадают.')
        
        return cleaned_data

class DocumentTypeForm(forms.ModelForm):
    class Meta:
        model = DocumentType
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter document type name')
            })
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if DocumentType.objects.filter(name__iexact=name).exclude(id=self.instance.id).exists():
            raise forms.ValidationError(_('A document type with this name already exists'))
        return name 