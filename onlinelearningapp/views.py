from django.shortcuts import render, redirect
from django.contrib.auth.models import User
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

    return render(request, 'onlinelearning/register.html')
