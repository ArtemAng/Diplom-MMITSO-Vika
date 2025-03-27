from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            messages.error(request, "У вас нет прав для выполнения этого действия.")
            return redirect('profile')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap 