from django.utils import timezone
from datetime import timedelta
from .models import Document, Notification
from django.db.models import Q

def check_expiring_documents():
    """
    Проверяет документы, срок действия которых истекает в ближайшие 10 дней,
    и создает уведомления для пользователей.
    """
    # Получаем текущую дату
    today = timezone.now().date()
    
    # Находим документы, срок действия которых истекает в ближайшие 10 дней
    expiring_documents = Document.objects.filter(
        expiry_date__isnull=False,
        expiry_date__lte=today + timedelta(days=10)
    )
    
    # Для каждого документа создаем уведомление
    for document in expiring_documents:
        # Проверяем, не существует ли уже уведомление для этого документа
        if not Notification.objects.filter(
            document=document,
            notification_date=today,
            is_sent=False
        ).exists():
            # Вычисляем количество дней до истечения срока
            days_until_expiry = (document.expiry_date - today).days
            
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
            Notification.objects.create(
                user=document.user,
                document=document,
                notification_date=today,
                message=message,
                is_sent=False
            ) 