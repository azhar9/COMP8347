from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .models import Role, UserProfile


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        # Create a new User object
        user = User.objects.create_user(username=username, email=email, password=password)

        # Get the Role object based on the selected role
        role_obj = Role.objects.get(name=role)

        # Create a UserProfile object
        UserProfile.objects.create(user=user, role=role_obj)
        return redirect('home')  # Redirect to the home page after successful registration

    return render(request, 'register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the home page after successful login
        else:
            error_message = 'Invalid username or password.'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')


def forgot_password(request):
    if request.method == 'POST':
        # Pass the request to Django's PasswordResetView
        return auth_views.PasswordResetView.as_view(
            template_name='forgot_password.html',
            email_template_name='password_reset_email.html',
            success_url=reverse_lazy('password_reset_done')
        )(request)
    else:
        return render(request, 'forgot_password.html')


def index(request):
    return render(request, 'login.html')


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'home.html')
