import os
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.ForeignKey('Role', on_delete=models.CASCADE, null=True, blank=True)

    objects = UserManager()

    @property
    def unread_notifications_count(self):
        count = self.notifications.filter(is_sent=False).count()
        print(f"User {self.username} has {count} unread notifications")
        return count

    def __str__(self):
        return self.username

# Роли пользователей
class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class DocumentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# Документы
class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    file_path = models.FileField(upload_to='documents/')
    original_filename = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.document_type.name} - {self.original_filename or self.file_path.name}"

# Логи документов
class DocumentLog(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="logs")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    changes = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document} - {self.action}"

# Уведомления
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='notifications')
    notification_date = models.DateField()
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return f"Уведомление для {self.user.username} о документе {self.document.original_filename}"
