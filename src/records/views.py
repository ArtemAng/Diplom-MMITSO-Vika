from rest_framework import viewsets
from .models import Role, User, DocumentType, Document, DocumentLog, Notification
from .serializers import RoleSerializer, UserSerializer, DocumentTypeSerializer, DocumentSerializer, DocumentLogSerializer, NotificationSerializer
from django.shortcuts import render, redirect
from .forms import LoginForm, RegistrationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile') 
    else:
        form = LoginForm()
    
    return render(request, 'registration/login.html', {'form': form})

def sign_up_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect("profile")
    else:
        form = RegistrationForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def profile_view(request):
    documents = Document.objects.filter(user=request.user)
    return render(request, 'records/profile.html', {'documents': documents})