from rest_framework import serializers
from .models import Role, User, DocumentType, Document, DocumentLog, Notification

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    # role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())

    class Meta:
        model = User
        fields = '__all__'


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    document_type = serializers.PrimaryKeyRelatedField(queryset=DocumentType.objects.all())

    class Meta:
        model = Document
        fields = '__all__'


# TODO:
# Логи сделать программно и автоматически
class DocumentLogSerializer(serializers.ModelSerializer):
    document = DocumentSerializer()
    user = UserSerializer()

    class Meta:
        model = DocumentLog
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    document = DocumentSerializer()

    class Meta:
        model = Notification
        fields = '__all__'
