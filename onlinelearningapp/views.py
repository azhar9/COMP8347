from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import Role, UserProfile


# TODO: use class based views
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
        email = request.POST['email']

        # Check if the email exists in the User model
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            # Generate the password reset token and URL
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            current_site = get_current_site(request)
            reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            reset_url = f"{request.scheme}://{current_site}{reset_url}"
            print("reset_url", reset_url)

            # Render the email template with the reset URL
            email_subject = 'Password reset OnlineLearning'
            email_message = render_to_string('password_reset_email.html', {
                'user': user,
                'password_reset_url': reset_url,
            })

            # Send the email using your preferred email sending method
            # For example, using Django's EmailMessage class:
            from django.core.mail import EmailMessage
            email = EmailMessage(email_subject, email_message, to=[user.email])
            email.send()

            return redirect('password_reset_done')
        else:
            messages.error(request, 'No user with that email address exists.')
            return redirect('forgot_password')
    else:
        return render(request, 'forgot_password.html')


def index(request):
    return redirect('login_view')


def home(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    return render(request, 'home.html')
