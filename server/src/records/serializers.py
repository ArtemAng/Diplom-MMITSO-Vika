from rest_framework import serializers
from .models import Role, User, DocumentType, Document, DocumentLog, Notification

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())

    class Meta:
        model = User
        fields = '__all__'


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    document_type = DocumentTypeSerializer()

    class Meta:
        model = Document
        fields = '__all__'

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
