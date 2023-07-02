"""
URL configuration for onlinelearning project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from onlinelearningapp.views import register, HomeView, login_view, forgot_password, index, CourseView, \
    CourseDetailView, SectionView, AddSectionView, AddContentView, ProfileView, enrollCourse, CourseNavigationView
urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('register/', register, name='register'),
    path('home/', HomeView.as_view(), name='home'),
    path('login/', login_view, name='login_view'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login_view'), name='logout'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('password-reset/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
    path('create-course/', CourseView.as_view(), name='create_course'),
    path('courses/<courseid>', CourseDetailView.as_view(), name='course_detail'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('enrollCourse.do', enrollCourse, name='enrollCourse'),
    path('courses/<int:courseid>/add-section/', AddSectionView.as_view(), name='add_section'),
    path('courses/<int:courseid>/<int:sectionid>/', SectionView.as_view(), name='section_detail'),
    path('courses/<int:courseid>/<int:sectionid>/add-content/', AddContentView.as_view(), name='add_content'),
    path('courses/<int:courseid>/<int:sectionid>/<int:coursecontentid>', AddContentView.as_view(), name='add_content'),
    path('course_navigation/<int:course_id>', CourseNavigationView.as_view(), name='course_navigation'),
]
