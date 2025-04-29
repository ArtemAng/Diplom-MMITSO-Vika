from rest_framework import viewsets
from django.contrib.auth import get_user_model
from .models import Role, DocumentType, Document, DocumentLog, Notification
from .serializers import RoleSerializer, UserSerializer, DocumentTypeSerializer, DocumentSerializer, DocumentLogSerializer, NotificationSerializer
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, SignupForm, DocumentForm, DocumentTypeForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import FileResponse, Http404, JsonResponse
from .decorators import admin_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
import os
import uuid
from django.utils import timezone
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
import json
from django.utils import translation

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
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            agree_policy = form.cleaned_data['agree_policy']
            
            if password1 != password2:
                messages.error(request, 'Пароли не совпадают.')
                return render(request, 'records/signup.html', {'form': form})
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Пользователь с таким именем уже существует.')
                return render(request, 'records/signup.html', {'form': form})
            
            if not agree_policy:
                messages.error(request, 'Для регистрации необходимо согласиться с пользовательским соглашением.')
                return render(request, 'records/signup.html', {'form': form})
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('profile')
    else:
        form = SignupForm()
    return render(request, 'records/signup.html', {'form': form})

@login_required
def profile_view(request):
    documents_list = Document.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(documents_list, 10)
    page = request.GET.get('page', 1)
    try:
        documents = paginator.page(page)
    except:
        documents = paginator.page(1)
    return render(request, 'records/profile.html', {
        'documents': documents,
        'total_count': documents_list.count()
    })

@login_required
def add_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            
            # Сохраняем оригинальное имя файла
            if 'file_path' in request.FILES:
                document.original_filename = request.FILES['file_path'].name
            
            # Генерируем уникальное имя файла
            if 'file_path' in request.FILES:
                file = request.FILES['file_path']
                ext = os.path.splitext(file.name)[1]
                filename = f"{request.user.username}/{uuid.uuid4()}{ext}"
                document.file_path.name = f"documents/{filename}"
            
            document.save()
            
            # Проверяем, истекает ли срок действия документа в ближайшие 10 дней
            if document.expiry_date:
                today = timezone.now().date()
                days_until_expiry = (document.expiry_date - today).days
                
                messages.info(request, f'Дней до истечения срока: {days_until_expiry}')
                
                if days_until_expiry <= 10:  # Убрали проверку на 0, так как документ может быть просрочен
                    # Создаем сообщение в зависимости от количества дней
                    if days_until_expiry < 0:
                        message = f"Срок действия документа '{document.original_filename}' истек!"
                    elif days_until_expiry == 0:
                        message = f"Срок действия документа '{document.original_filename}' истекает сегодня!"
                    elif days_until_expiry == 1:
                        message = f"Срок действия документа '{document.original_filename}' истекает завтра!"
                    else:
                        message = f"Срок действия документа '{document.original_filename}' истекает через {days_until_expiry} дней!"
                    
                    # Создаем уведомление
                    notification = Notification.objects.create(
                        user=request.user,
                        document=document,
                        notification_date=today,
                        message=message,
                        is_sent=False
                    )
                    
                    messages.info(request, f'Создано уведомление: {message}')
            
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
        print(document.file_path.path)
        file_path = document.file_path.path 
        response = FileResponse(open(file_path, 'rb'), as_attachment=True)
        return response

    except Document.DoesNotExist:
        raise Http404("Документ не найден.")

@login_required
def edit_document(request, document_id):
    document = get_object_or_404(Document, id=document_id, user=request.user)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            # Если новый файл не загружен, сохраняем старое имя файла
            if 'file_path' not in request.FILES:
                form.instance.file_path = document.file_path
            form.save()
            messages.success(request, 'Документ успешно обновлен')
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
    """
    Управление типами документов: создание, редактирование, удаление.
    """
    if request.method == 'POST':
        form = DocumentTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тип документа успешно добавлен.')
            return redirect('manage_document_types')
    else:
        form = DocumentTypeForm()
    
    # Поиск по названию
    search_query = request.GET.get('search', '')
    document_types_list = DocumentType.objects.all()
    
    if search_query:
        document_types_list = document_types_list.filter(name__icontains=search_query)
    
    # Сортировка
    sort_by = request.GET.get('sort', 'name')
    if sort_by == '-name':
        document_types_list = document_types_list.order_by('-name')
    else:
        document_types_list = document_types_list.order_by('name')
    
    # Пагинация
    paginator = Paginator(document_types_list, 10)
    page = request.GET.get('page', 1)
    
    try:
        document_types = paginator.page(page)
    except PageNotAnInteger:
        document_types = paginator.page(1)
    except EmptyPage:
        document_types = paginator.page(paginator.num_pages)
    
    context = {
        'form': form,
        'document_types': document_types,
        'total_count': document_types_list.count(),
        'search_query': search_query,
        'current_sort': sort_by
    }
    
    return render(request, 'records/manage_document_types.html', context)

@login_required
@admin_required
def edit_document_type(request, type_id):
    """
    Редактирование типа документа.
    """
    document_type = get_object_or_404(DocumentType, id=type_id)
    
    if request.method == 'POST':
        form = DocumentTypeForm(request.POST, instance=document_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тип документа успешно обновлен.')
            return redirect('manage_document_types')
    else:
        form = DocumentTypeForm(instance=document_type)
    
    return render(request, 'records/edit_document_type.html', {
        'form': form,
        'document_type': document_type
    })

@login_required
@admin_required
def delete_document_type(request, type_id):
    """
    Удаление типа документа с подтверждением.
    """
    document_type = get_object_or_404(DocumentType, id=type_id)
    
    # Проверяем, есть ли документы данного типа
    documents_count = Document.objects.filter(document_type=document_type).count()
    
    if request.method == 'POST':
        document_type.delete()
        messages.success(request, f'Тип документа "{document_type.name}" успешно удален.')
        return redirect('manage_document_types')
    
    return render(request, 'records/confirm_delete_document_type.html', {
        'document_type': document_type,
        'documents_count': documents_count
    })

@login_required
@admin_required
def admin_documents(request):
    """
    Представление для управления документами в панели администратора.
    Включает поиск, фильтрацию и сортировку.
    """
    documents_list = Document.objects.all().select_related('user', 'document_type')
    
    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        documents_list = documents_list.filter(
            Q(original_filename__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(document_type__name__icontains=search_query)
        )
    
    # Фильтрация по типу документа
    document_type_filter = request.GET.get('document_type')
    if document_type_filter:
        documents_list = documents_list.filter(document_type_id=document_type_filter)
    
    # Фильтрация по пользователю
    user_filter = request.GET.get('user')
    if user_filter:
        documents_list = documents_list.filter(user_id=user_filter)
    
    # Фильтрация по сроку действия
    expiry_filter = request.GET.get('expiry')
    today = timezone.now().date()
    if expiry_filter == 'expired':
        documents_list = documents_list.filter(expiry_date__lt=today)
    elif expiry_filter == 'expiring_soon':
        documents_list = documents_list.filter(
            expiry_date__gte=today,
            expiry_date__lte=today + timezone.timedelta(days=10)
        )
    elif expiry_filter == 'valid':
        documents_list = documents_list.filter(expiry_date__gt=today)
    
    # Сортировка
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['created_at', '-created_at', 'original_filename', '-original_filename', 
                  'user__username', '-user__username', 'document_type__name', '-document_type__name',
                  'expiry_date', '-expiry_date']:
        documents_list = documents_list.order_by(sort_by)
    
    # Пагинация
    paginator = Paginator(documents_list, 10)
    page = request.GET.get('page', 1)
    
    try:
        documents = paginator.page(page)
    except PageNotAnInteger:
        documents = paginator.page(1)
    except EmptyPage:
        documents = paginator.page(paginator.num_pages)
    
    # Получаем списки для фильтров
    document_types = DocumentType.objects.all()
    users = User.objects.all()
    
    context = {
        'documents': documents,
        'document_types': document_types,
        'users': users,
        'search_query': search_query,
        'current_document_type': document_type_filter,
        'current_user': user_filter,
        'current_expiry': expiry_filter,
        'current_sort': sort_by,
        'total_count': documents_list.count()
    }
    
    return render(request, 'records/admin_documents.html', context)

@login_required
@admin_required
def admin_delete_document(request, document_id):
    """
    Удаление документа администратором с подтверждением.
    """
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, f'Документ "{document.original_filename}" успешно удален.')
        return redirect('admin_documents')
    
    return render(request, 'records/confirm_admin_delete_document.html', {'document': document})

@login_required
@admin_required
def admin_users(request):
    """
    Отображение списка пользователей с возможностью поиска и фильтрации.
    """
    # Получаем параметры фильтрации и поиска
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', '-date_joined')
    
    # Базовый запрос
    users_list = User.objects.all()
    
    # Применяем поиск
    if search_query:
        users_list = users_list.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Применяем фильтр по роли
    if role_filter:
        if role_filter == 'admin':
            users_list = users_list.filter(is_staff=True)
        elif role_filter == 'user':
            users_list = users_list.filter(is_staff=False)
    
    # Применяем фильтр по статусу
    if status_filter:
        if status_filter == 'active':
            users_list = users_list.filter(is_active=True)
        elif status_filter == 'inactive':
            users_list = users_list.filter(is_active=False)
    
    # Применяем сортировку
    users_list = users_list.order_by(sort_by)
    
    # Пагинация
    paginator = Paginator(users_list, 10)
    page = request.GET.get('page', 1)
    try:
        users = paginator.page(page)
    except:
        users = paginator.page(1)
    
    # Получаем все роли для фильтра
    roles = Role.objects.all()
    
    # Контекст для шаблона
    context = {
        'users': users,
        'roles': roles,
        'search_query': search_query,
        'current_role': role_filter,
        'current_status': status_filter,
        'current_sort': sort_by,
        'total_users': users_list.count(),
    }
    
    return render(request, 'records/admin_users.html', context)

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

@login_required
@user_passes_test(lambda u: u.is_staff)
def toggle_admin(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            if user != request.user:  # Предотвращаем отзыв прав у самого себя
                user.is_staff = not user.is_staff
                user.save()
                messages.success(request, f'Права администратора {"предоставлены" if user.is_staff else "отозваны"} у пользователя {user.username}')
            else:
                messages.error(request, 'Вы не можете изменить свои собственные права администратора')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
    return redirect('admin_users')

def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('login')

@login_required
def notifications(request):
    """
    Отображает уведомления пользователя с пагинацией.
    """
    # Получаем все уведомления пользователя
    notifications_list = Notification.objects.filter(user=request.user).order_by('-notification_date', '-created_at')
    
    # Создаем объект пагинатора, 10 уведомлений на страницу
    paginator = Paginator(notifications_list, 10)
    
    # Получаем номер текущей страницы из GET-параметра
    page = request.GET.get('page', 1)
    
    try:
        # Получаем объекты для текущей страницы
        notifications = paginator.page(page)
    except:
        # Если что-то пошло не так, показываем первую страницу
        notifications = paginator.page(1)
    
    return render(request, 'records/notifications.html', {
        'notifications': notifications,
        'total_count': notifications_list.count()
    })

@login_required
@staff_member_required
def admin_notifications(request):
    """
    Представление для управления уведомлениями в панели администратора.
    Администраторы могут видеть все уведомления, но могут отмечать как прочитанные только свои.
    """
    notifications = Notification.objects.all().select_related('user', 'document').order_by('-created_at')
    
    # Фильтрация по пользователю
    user_filter = request.GET.get('user')
    if user_filter:
        notifications = notifications.filter(user__username__icontains=user_filter)
    
    # Фильтрация по статусу
    status_filter = request.GET.get('status')
    if status_filter in ['read', 'unread']:
        notifications = notifications.filter(is_sent=(status_filter == 'read'))
    
    # Пагинация
    paginator = Paginator(notifications, 10)
    page = request.GET.get('page', 1)
    
    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)
    
    # Получаем список всех пользователей для фильтра
    users = User.objects.all().values('username').distinct()
    
    context = {
        'notifications': notifications,
        'users': users,
        'current_user_filter': user_filter,
        'current_status_filter': status_filter,
    }
    
    return render(request, 'records/admin_notifications.html', context)

@login_required
@staff_member_required
def admin_delete_notification(request, notification_id):
    """
    Удаление уведомления администратором.
    """
    notification = get_object_or_404(Notification, id=notification_id)
    notification.delete()
    messages.success(request, 'Уведомление успешно удалено.')
    return redirect('admin_notifications')

@login_required
@staff_member_required
def admin_mark_notification_read(request, notification_id):
    """
    Отметка уведомления как прочитанного администратором.
    Администратор может отмечать как прочитанные только свои уведомления.
    """
    notification = get_object_or_404(Notification, id=notification_id)
    
    if notification.user == request.user:
        notification.is_sent = True
        notification.save()
        messages.success(request, 'Уведомление отмечено как прочитанное.')
    else:
        messages.error(request, 'Вы можете отмечать как прочитанные только свои уведомления.')
    
    return redirect('admin_notifications')

def privacy_policy_view(request):
    """
    Представление для отображения страницы пользовательского соглашения
    """
    return render(request, 'records/privacy_policy.html')