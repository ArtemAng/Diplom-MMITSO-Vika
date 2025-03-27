from rest_framework import viewsets
from django.contrib.auth import get_user_model
from .models import Role, DocumentType, Document, DocumentLog, Notification
from .serializers import RoleSerializer, UserSerializer, DocumentTypeSerializer, DocumentSerializer, DocumentLogSerializer, NotificationSerializer
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, SignupForm, DocumentForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from .decorators import admin_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

User = get_user_model()

def handler404(request, exception):
    if request.user.is_authenticated:
        return redirect('profile')
    return redirect('login')

def home_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    return redirect('login')

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class DocumentTypeViewSet(viewsets.ModelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class DocumentLogViewSet(viewsets.ModelViewSet):
    queryset = DocumentLog.objects.all()
    serializer_class = DocumentLogSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = LoginForm()
    return render(request, 'records/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            
            if password1 != password2:
                messages.error(request, 'Пароли не совпадают.')
                return render(request, 'records/signup.html', {'form': form})
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Пользователь с таким именем уже существует.')
                return render(request, 'records/signup.html', {'form': form})
            
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('profile')
    else:
        form = SignupForm()
    return render(request, 'records/signup.html', {'form': form})

@login_required
def profile_view(request):
    documents = Document.objects.filter(user=request.user)
    return render(request, 'records/profile.html', {'documents': documents})

@login_required
def add_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            messages.success(request, 'Документ успешно добавлен.')
            return redirect('profile')
    else:
        form = DocumentForm()
    
    return render(request, 'records/add_document.html', {'form': form})

@login_required
def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id, user=request.user)
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Документ успешно удален.')
        return redirect('profile')
    return render(request, 'records/confirm_delete.html', {'document': document})

@login_required
def download_document(request, document_id):
    try:
        document = Document.objects.get(id=document_id)
        file_path = document.file_path.path 
        response = FileResponse(open(file_path, 'rb'), as_attachment=True)
        return response

    except Document.DoesNotExist:
        raise Http404("Документ не найден.")

@login_required
def edit_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = DocumentForm(instance=document)

    return render(request, 'records/edit_document.html', {'form': form, 'document': document})

@login_required
@admin_required
def admin_dashboard(request):
    users = User.objects.all()
    documents = Document.objects.all()
    document_types = DocumentType.objects.all()
    return render(request, 'records/admin_dashboard.html', {
        'users': users,
        'documents': documents,
        'document_types': document_types
    })

@login_required
@admin_required
def manage_users(request):
    users = User.objects.all()
    return render(request, 'records/manage_users.html', {'users': users})

@login_required
@admin_required
def manage_document_types(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            DocumentType.objects.create(name=name)
    document_types = DocumentType.objects.all()
    return render(request, 'records/manage_document_types.html', {'document_types': document_types})

@login_required
@admin_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('manage_users')
    return render(request, 'records/confirm_delete_user.html', {'user': user})

@login_required
@admin_required
def delete_document_type(request, type_id):
    doc_type = get_object_or_404(DocumentType, id=type_id)
    if request.method == 'POST':
        doc_type.delete()
        return redirect('manage_document_types')
    return render(request, 'records/confirm_delete_document_type.html', {'doc_type': doc_type})

@login_required
@admin_required
def admin_documents(request):
    # Получаем параметры фильтрации и поиска
    search_query = request.GET.get('search', '')
    user_filter = request.GET.get('user', '')
    doc_type_filter = request.GET.get('doc_type', '')
    
    # Базовый queryset
    documents = Document.objects.all().select_related('user', 'document_type')
    
    # Применяем фильтры
    if search_query:
        documents = documents.filter(
            Q(user__username__icontains=search_query) |
            Q(document_type__name__icontains=search_query)
        )
    
    if user_filter:
        documents = documents.filter(user_id=user_filter)
    
    if doc_type_filter:
        documents = documents.filter(document_type_id=doc_type_filter)
    
    # Сортируем по дате загрузки (новые сверху)
    documents = documents.order_by('-uploaded_at')
    
    # Пагинация
    paginator = Paginator(documents, 10)  # 10 документов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Получаем списки для фильтров
    users = User.objects.all()
    document_types = DocumentType.objects.all()
    
    context = {
        'documents': page_obj,
        'users': users,
        'document_types': document_types,
        'search_query': search_query,
        'selected_user': user_filter,
        'selected_doc_type': doc_type_filter,
        'is_paginated': True,
        'page_obj': page_obj,
    }
    
    return render(request, 'records/admin_documents.html', context)

@login_required
@admin_required
def admin_delete_document(request, document_id):
    try:
        document = Document.objects.get(id=document_id)
        if request.method == 'POST':
            document.delete()
            messages.success(request, 'Документ успешно удален.')
            return redirect('admin_documents')
        return render(request, 'records/confirm_admin_delete.html', {'document': document})
    except Document.DoesNotExist:
        messages.error(request, 'Документ не найден или уже удален.')
        return redirect('admin_documents')

@login_required
@admin_required
def admin_users(request):
    users = User.objects.all()
    return render(request, 'records/admin_users.html', {'users': users})

@login_required
@admin_required
def admin_delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        if request.method == 'POST':
            user.delete()
            messages.success(request, 'Пользователь успешно удален.')
            return redirect('admin_users')
        return render(request, 'records/confirm_admin_delete_user.html', {'user': user})
    except User.DoesNotExist:
        messages.error(request, 'Пользователь не найден или уже удален.')
        return redirect('admin_users')

def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('login')