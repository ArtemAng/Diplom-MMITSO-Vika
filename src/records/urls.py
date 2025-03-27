from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RoleViewSet, UserViewSet, DocumentTypeViewSet, DocumentViewSet, 
    DocumentLogViewSet, NotificationViewSet, download_document, edit_document, 
    login_view, sign_up_view, delete_document, profile_view, add_document,
    admin_dashboard, manage_users, manage_document_types, delete_user, delete_document_type,
    home_view, admin_documents, admin_delete_document
)
from django.contrib.auth import views as auth_views

router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'users', UserViewSet)
router.register(r'document_types', DocumentTypeViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'document_logs', DocumentLogViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', home_view, name='home'),
    path('api/', include(router.urls)),
    path('login/', login_view, name='login'),
    path('signup/', sign_up_view, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/', http_method_names=['post', 'get']), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('add_document/', add_document, name='add_document'),
    path('delete_document/<int:document_id>/', delete_document, name='delete_document'),
    path('download/<int:document_id>/', download_document, name='download_document'),
    path('edit/<int:document_id>/', edit_document, name='edit_document'),
    
    # Административные URL-маршруты
    path('admin-panel/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', manage_users, name='manage_users'),
    path('admin-panel/users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('admin-panel/document-types/', manage_document_types, name='manage_document_types'),
    path('admin-panel/document-types/delete/<int:type_id>/', delete_document_type, name='delete_document_type'),
    path('admin-panel/documents/', admin_documents, name='admin_documents'),
    path('admin-panel/documents/delete/<int:document_id>/', admin_delete_document, name='admin_delete_document'),
]
