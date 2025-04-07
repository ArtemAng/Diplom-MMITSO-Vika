from django.core.management.base import BaseCommand
from records.tasks import check_expiring_documents

class Command(BaseCommand):
    help = 'Проверяет документы, срок действия которых истекает в ближайшие 10 дней'
 
    def handle(self, *args, **options):
        self.stdout.write('Начинаем проверку документов...')
        check_expiring_documents()
        self.stdout.write(self.style.SUCCESS('Проверка документов завершена')) 