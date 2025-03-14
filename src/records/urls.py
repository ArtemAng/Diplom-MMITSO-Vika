from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, UserViewSet, DocumentTypeViewSet, DocumentViewSet, DocumentLogViewSet, NotificationViewSet, download_document, edit_document, login_view, sign_up_view, delete_document, profile_view, add_document
from django.contrib.auth import views as auth_views

router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'users', UserViewSet)
router.register(r'document_types', DocumentTypeViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'document_logs', DocumentLogViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('login/', login_view, name='login'),
    path('signup/', sign_up_view, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), # Тут надо чекнуть не забыл ли 4о
    path('profile/', profile_view, name='profile'),
    path('add_document/', add_document, name='add_document'),
    path('delete_document/<int:document_id>/', delete_document, name='delete_document'),
    path('download/<int:document_id>/', download_document, name='download_document'),
    path('edit/<int:document_id>/', edit_document, name='edit_document'),
]
