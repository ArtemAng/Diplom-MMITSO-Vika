from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def timeuntil_days(value):
    """
    Возвращает количество дней до указанной даты.
    """
    if not value:
        return 0
    
    today = timezone.now().date()
    delta = value - today
    return delta.days 