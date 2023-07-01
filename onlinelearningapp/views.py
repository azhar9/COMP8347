from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View

from .models import Role, UserProfile, Course, Membership, Section, CourseContent


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


# TODO: create different home page templates for both students and teacher
class HomeView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login_view')
        
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.role.name == "teacher":
            #teacher home page
            course_list = Course.objects.all()
            context = {'course_list': course_list}
            print(course_list)
            return render(request, 'home_teacher.html', context)

        return render(request, 'home_student.html')


class CourseView(View):
    template_name = 'course_builder.html'
    def get(self, request):
        course_list = Course.objects.filter(instructor_id=request.user.id)
        context = {'course_list': course_list}
        return render(request, self.template_name, context)

    def post(self, request):
        name = request.POST.get('name')
        description = request.POST.get('description')
        membership = request.POST.get('membership_level_required')
        description = request.POST.get('description')
        instructor_id = request.user.id

        instructor = User.objects.get(id=instructor_id)
        membership_level_required = Membership.objects.get(name=membership)

        # Create the course and associate it with the instructor
        course = Course.objects.create(
            name=name,
            description=description,
            membership_level_required=membership_level_required,
            instructor=instructor,
        )

        return redirect('home')


class CourseDetailView(View):
    def get(self, request, courseid):
        #TODO: get an object here with section and their respective content
        print(courseid)
        course = get_object_or_404(Course, id=courseid)
        sections = Section.objects.filter(course=course)
        context = {
            'course': course,
            'sections': sections
        }
        print(context)
        return render(request, 'course_detail.html', context)


class AddSectionView(View):
    def get(self, request, courseid):
        course = get_object_or_404(Course, id=courseid)
        context = {
            'course': course,
        }
        return render(request, 'add_section.html', context)

    def post(self, request, courseid):
        course = get_object_or_404(Course, id=courseid)
        order = Section.objects.filter(course=course).count()

        name = request.POST.get('name')
        description = request.POST.get('description')

        print(Course, name, description, order)

        section = Section.objects.create(
            name=name,
            description=description,
            order=order+1,
            course=course
        )

        return redirect('course_detail', courseid=courseid)


class SectionView(View):
    def get(self, request, courseid, sectionid):
        print('hi', courseid, sectionid)
        course = get_object_or_404(Course, id=courseid)
        section = get_object_or_404(Section, id=sectionid)
        contents = CourseContent.objects.filter(section=section)
        context = {
            'section': section,
            'course': course,
            'contents': contents
        }
        return render(request, 'section_detail.html', context)
    

class CourseContentView(View):
    def get(self, request, courseid, sectionid, coursecontentid):
        section = get_object_or_404(Section, id=sectionid)
        course = get_object_or_404(Course, id=courseid)
        coursecontent = get_object_or_404(CourseContent, id=coursecontentid)
        context = {
            'section': section,
            'course': course,
            'coursecontent': coursecontent
        }
        return render(request, 'section_detail.html', context)
    


class AddContentView(View):
    def get(self, request, courseid, sectionid):
        section = get_object_or_404(Section, id=sectionid)
        course = get_object_or_404(Course, id=courseid)
        context = {
            'section': section,
            'course': course,
        }
        return render(request, 'add_content.html', context)

    def post(self, request, courseid, sectionid):
        section = get_object_or_404(Section, id=sectionid)
        order = CourseContent.objects.filter(section=section).count()

        name = request.POST.get('name')
        content_file = request.FILES.get('file')
        content_type = request.POST.get('content_type')
        print("in post method", name, content_type, content_file, request.FILES)
        
        # Create the course content object
        course_content = CourseContent.objects.create(
            section=section,
            name=name,
            order=order+1,  # Set the filepath field
            filepath=content_file,
            content_type=content_type,
        )

        return redirect('section_detail', courseid=courseid, sectionid=sectionid)
