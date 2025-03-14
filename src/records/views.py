from rest_framework import viewsets
from .models import Role, User, DocumentType, Document, DocumentLog, Notification
from .serializers import RoleSerializer, UserSerializer, DocumentTypeSerializer, DocumentSerializer, DocumentLogSerializer, NotificationSerializer
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, RegistrationForm, DocumentForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404

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

@login_required
def add_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)  
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user  
            document.file_path = request.FILES['file_path']  
            document.save()
            return redirect('profile')
    else:
        form = DocumentForm()
    
    return render(request, 'records/add_document.html', {'form': form})

@login_required
def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id, user=request.user)
    if request.method == 'POST':
        document.delete()
        return redirect('profile')
    return render(request, 'confirm_delete.html', {'document': document})

@login_required
def download_document(request, document_id):
    try:
        document = Document.objects.get(id=document_id)
        file_path = document.file_path.path 
        response = FileResponse(open(file_path, 'rb'), as_attachment=True)
        return response

    except Document.DoesNotExist:
        raise Http404("Документ не найден.")

@login_required
def edit_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = DocumentForm(instance=document)

    return render(request, 'records/edit_document.html', {'form': form, 'document': document})