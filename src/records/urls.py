from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RoleViewSet, UserViewSet, DocumentTypeViewSet, DocumentViewSet, 
    DocumentLogViewSet, NotificationViewSet, download_document, edit_document, 
    login_view, signup_view, delete_document, profile_view, add_document,
    admin_dashboard, admin_documents, admin_delete_document, logout_view,
    admin_users, admin_delete_user, home_view, manage_document_types, toggle_admin
)
from django.contrib.auth import views as auth_views

router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'users', UserViewSet)
router.register(r'document-types', DocumentTypeViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'document-logs', DocumentLogViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', home_view, name='home'),
    path('api/', include(router.urls)),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('add_document/', add_document, name='add_document'),
    path('document/<int:document_id>/edit/', edit_document, name='edit_document'),
    path('document/<int:document_id>/delete/', delete_document, name='delete_document'),
    path('download/<int:document_id>/', download_document, name='download_document'),
    
    # Административные URL-маршруты
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-panel/documents/', admin_documents, name='admin_documents'),
    path('admin-panel/documents/delete/<int:document_id>/', admin_delete_document, name='admin_delete_document'),
    path('admin-panel/users/', admin_users, name='admin_users'),
    path('admin-panel/users/<int:user_id>/delete/', admin_delete_user, name='admin_delete_user'),
    path('manage-document-types/', manage_document_types, name='manage_document_types'),
    path('toggle-admin/<int:user_id>/', toggle_admin, name='toggle_admin'),
]
