from django.contrib import admin
from .models import Role, User, DocumentType, Document, DocumentLog, Notification

# Register your models here.
admin.site.register(Role)
admin.site.register(User)
admin.site.register(DocumentType)
admin.site.register(Document)
admin.site.register(DocumentLog)
admin.site.register(Notification)