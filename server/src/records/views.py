from rest_framework import viewsets
from .models import Role, Document, DocumentType, DocumentLog, Notification, User
from .serializers import RoleSerializer, DocumentSerializer, DocumentTypeSerializer, DocumentLogSerializer, NotificationSerializer, UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

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
