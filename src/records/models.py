from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Роли пользователей
class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        # user = self.model(username=username, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # role = Role.objects.first() 

        return self.create_user(username, email, password, **extra_fields)
        # return self.create_user(username, email, password, role=role, **extra_fields)

# Пользователи
class User(AbstractUser):
    email = models.EmailField(unique=True)
    # role = models.ForeignKey('Role', on_delete=models.CASCADE)

    objects = UserManager()

    def __str__(self):
        return self.username


# Типы документов
class DocumentType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# Документы
class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=255)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.document_type.name}"


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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    notification_date = models.DateField()
    message = models.TextField()
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"To: {self.user.username} - {self.message[:50]}"
