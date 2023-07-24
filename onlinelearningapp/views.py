import os
import uuid
from collections import OrderedDict
from datetime import datetime, date
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import pdfkit
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View

from onlinelearning import settings
from .models import Role, UserProfile, Course, Membership, Enrollment, Section, CourseContent, CourseProgress, \
    Certificate

from .certificate import PdfGen


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']
        existing_user = User.objects.filter(Q(username=username) | Q(email=email)).first()
        context = {"error": None}
        if existing_user:
            context = {
                "error": "username or email already exists!"
            }
            return render(request, 'register.html', context=context)
        # Create a new User object
        user = User.objects.create_user(username=username, email=email, password=password)

        # Get the Role object based on the selected role
        role_obj = Role.objects.get(name=role)

        # Create a UserProfile object
        UserProfile.objects.create(user=user, role=role_obj)
        return redirect('home')  # Redirect to the home page after successful registration

        return render(request, 'register.html', context=context)


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
            email_subject = 'Password reset Eduhub Online Learning'
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
    return redirect('login')

@login_required
def enrollCourse(request):
    course_id = request.GET['courseId']

    course_details = get_object_or_404(Course, id=course_id)
    print("Course details found")
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    print("Found the elements")
    print("Course membership Type", course_details.membership_level_required)
    print("User membership Type", user_profile.membership)
    try:
        if course_details.membership_level_required.name != user_profile.membership.name:
            if user_profile.membership.name == 'bronze':
                enrollments = Enrollment.objects.get(student_id=request.user.id, course_id=course_id)
            elif user_profile.membership.name == 'gold':
                course_enrollment = Enrollment()
                course_enrollment.course_id = course_id
                course_enrollment.student_id = request.user.id
                course_enrollment.save()
            else:
                if course_details.membership_level_required.name == 'gold':
                    enrollments = Enrollment.objects.get(student_id=request.user.id, course_id=course_id)
                else:
                    course_enrollment = Enrollment()
                    course_enrollment.course_id = course_id
                    course_enrollment.student_id = request.user.id
                    course_enrollment.save()
        else:
            # print("Enrollments found")
            course_enrollment = Enrollment()
            course_enrollment.course_id = course_id
            course_enrollment.student_id = request.user.id
            course_enrollment.save()

        return redirect('home')
    except Enrollment.DoesNotExist:
        print("Inside Does notExist error")
        context = {
            'user_profile': user_profile,
            'membership_selected': course_details.membership_level_required.name,
            'existing_membership': user_profile.membership.name,
            'today_date': date.today().isoformat()
        }
        return render(request, 'payment.html', context)

@login_required
def dropCourse(request):
    course_id = request.GET.get('courseId')
    student_id = request.user.id

    course_enrollment = Enrollment.objects.filter(course_id=course_id, student_id=student_id)
    course_enrollment.delete()

    return redirect('home')


@method_decorator(login_required, name="dispatch")
class HomeView(View):
    def get(self, request):

        user_profile = UserProfile.objects.get(user=request.user)
        course_list = Course.objects.filter(published=True)
        if user_profile.role.name == "teacher":
            # teacher home page
            courses_per_instructor = Course.objects.filter(instructor=request.user.id)
            print(request.user.id)
            context = {
                'course_list': courses_per_instructor,
                'user_profile': user_profile,
            }
            return render(request, 'home_teacher.html', context)
        else:
            enrollments = Enrollment.objects.filter(student_id=request.user.id)
            for enrollment in enrollments:
                course_progress_count = CourseProgress.objects.filter(enrollment=enrollment, status=True).count()
                course_contents_count = CourseContent.objects.filter(section__course_id=enrollment.course.id).count()
                enrollment.progress = 100
                if course_contents_count is not 0:
                    enrollment.progress = int((course_progress_count / course_contents_count) * 100)

            bronze_courses = []
            silver_courses = []
            gold_courses = []
            for course in course_list:
                if course.membership_level_required.name == "bronze":
                    bronze_courses.append(course)
                if course.membership_level_required.name == "silver":
                    silver_courses.append(course)
                if course.membership_level_required.name == "gold":
                    gold_courses.append(course)
            context = {
                'user_profile': user_profile,
                'bronze_courses': bronze_courses,
                'silver_courses': silver_courses,
                'gold_courses': gold_courses,
                'enrollments': enrollments,
            }
            return render(request, 'home_student.html', context)

@method_decorator(login_required, name="dispatch")
class ProfileView(View):
    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        context = {
            'user_profile': user_profile
        }
        return render(request, 'profile.html', context)


@method_decorator(login_required, name="dispatch")
class ChangeMembership(View):
    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        context = {
            'user_profile': user_profile,
        }
        return render(request, 'change_membership.html', context)
    
    def post(self, request):
        membership_name = request.POST.get('membership')
        user_profile = get_object_or_404(UserProfile, user=request.user)
        user_profile.membership = Membership.objects.get(name=membership_name)
        user_profile.save()
        return redirect('profile')


@method_decorator(login_required, name="dispatch")
class CourseView(View):
    template_name = 'course_builder.html'

    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        course_list = Course.objects.filter(instructor_id=request.user.id)

        context = {
            'course_list': course_list,
            'user_profile': user_profile,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        name = request.POST.get('name')
        description = request.POST.get('description')
        membership = request.POST.get('membership_level_required')
        description = request.POST.get('description')
        instructor_id = request.user.id

        instructor = User.objects.get(id=instructor_id)
        membership_level_required = Membership.objects.get(name=membership)
        course = Course.objects.create(
            name=name,
            description=description,
            membership_level_required=membership_level_required,
            instructor=instructor,
        )

        return redirect('home')


@method_decorator(login_required, name="dispatch")
class CourseDetailView(View):
    def get(self, request, courseid):
        course = get_object_or_404(Course, id=courseid)

        user_profile = UserProfile.objects.get(user_id=request.user.id)
        print(user_profile.membership.name)
        courseEnrollmentsCounter = 0
        try:
            courseEnrollmentsCounter = len(Enrollment.objects.filter(course_id=courseid))
        except:
            pass

        try:
            enrollments = Enrollment.objects.get(student_id=request.user.id, course_id=courseid)
        except Enrollment.DoesNotExist:
            enrollments = None
        sections = Section.objects.filter(course=course)
        section_ids = [section.id for section in sections]
        contentExists = False
        # print(f"my content is :{CourseContent.objects.filter(section__in=section_ids)}")
        try:
            if len(CourseContent.objects.filter(section__in=section_ids)) > 0:
                contentExists = True
        except:
            pass
        context = {
            'course': course,
            'sections': sections,
            'user_profile': user_profile,
            'enrollments': enrollments,
            'courseEnrollements': courseEnrollmentsCounter,
            'contentExists': contentExists
        }
        print(context)
        return render(request, 'course_detail.html', context)

    def post(self, request, courseid):
        course = get_object_or_404(Course, id=courseid)
        if request.POST.get('publish').lower() == 'publish':
            course.published = True
        else:
            course.published = False
        course.save()
        return redirect('course_detail', courseid=courseid)


@method_decorator(login_required, name="dispatch")
class AddSectionView(View):
    def get(self, request, courseid):
        course = get_object_or_404(Course, id=courseid)
        user_profile = UserProfile.objects.get(user_id=request.user.id)
        context = {
            'course': course,
            'user_profile': user_profile
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
            order=order + 1,
            course=course
        )

        return redirect('course_detail', courseid=courseid)


@method_decorator(login_required, name="dispatch")
class SectionView(View):
    def get(self, request, courseid, sectionid):
        print('hi', courseid, sectionid)
        user_profile = UserProfile.objects.get(user_id=request.user.id)
        course = get_object_or_404(Course, id=courseid)
        section = get_object_or_404(Section, id=sectionid)
        contents = CourseContent.objects.filter(section=section)
        context = {
            'section': section,
            'course': course,
            'contents': contents,
            'role': user_profile.role.name,
            'user_profile': user_profile

        }
        return render(request, 'section_detail.html', context)


@method_decorator(login_required, name="dispatch")
class CourseContentView(View):
    def get(self, request, courseid, sectionid, coursecontentid):
        user_profile = UserProfile.objects.get(user_id=request.user.id)
        section = get_object_or_404(Section, id=sectionid)
        course = get_object_or_404(Course, id=courseid)
        coursecontent = get_object_or_404(CourseContent, id=coursecontentid)
        context = {
            'section': section,
            'course': course,
            'coursecontent': coursecontent,
            'user_profile': user_profile,
        }
        return render(request, 'section_detail.html', context)


@method_decorator(login_required, name="dispatch")
class AddContentView(View):
    def get(self, request, courseid, sectionid):
        user_profile = UserProfile.objects.get(user_id=request.user.id)
        section = get_object_or_404(Section, id=sectionid)
        course = get_object_or_404(Course, id=courseid)
        context = {
            'section': section,
            'course': course,
            'role': 'teacher',
            'user_profile': user_profile,
        }
        return render(request, 'add_content.html', context)

    def post(self, request, courseid, sectionid):
        section = get_object_or_404(Section, id=sectionid)
        order = CourseContent.objects.filter(section=section).count()

        name = request.POST.get('name')
        content_file = request.FILES.get('file')
        content_type = request.POST.get('content_type')
        role = request.POST.get('role')
        print("in post method", name, content_type, content_file, request.FILES)

        # Create the course content object
        course_content = CourseContent.objects.create(
            section=section,
            name=name,
            order=order + 1,
            filepath=content_file,
            content_type=content_type,
        )

        return redirect('section_detail', courseid=courseid, sectionid=sectionid)

@method_decorator(login_required, name="dispatch")
class CourseNavigationView(View):
    def get(self, request, courseid, coursecontentid=None):
        user_profile = UserProfile.objects.get(user_id=request.user.id)
        course = get_object_or_404(Course, id=courseid)
        if user_profile.role.name == 'teacher':
            course_content = get_object_or_404(CourseContent, id=coursecontentid)
            # get the current section, its data and return
            contents = {
                course_content.section.name: [
                    course_content
                ]
            }
            context = {
                'user_profile': user_profile,
                'contents': contents,
                'section': course_content.section,
                'course': course,
                'coursecontent': course_content
            }
            return render(request, 'course_navigation.html', context)

        enrollment = Enrollment.objects.get(student_id=request.user.id, course_id=courseid)
        section_list = list(course.section_set.all().order_by('order'))
        # Get all the course contents related to the sections
        contents = OrderedDict()
        for sect in section_list:
            contents[sect.name] = list(sect.coursecontent_set.all())
            content_list = []
            for content in sect.coursecontent_set.all():
                try:
                    course_progress = CourseProgress.objects.get(course_content=content, enrollment=enrollment)
                    content.is_completed = course_progress.status
                except:
                    content.is_completed = False
                content_list.append(content)
            contents[sect.name] = content_list

        # if contentid is not specified, then redirect to the first content in first section
        if coursecontentid is None:
            # TODO: skip to first non-complete content instead of always taking first. If all contents are complete, display download certi page
            section = next(iter(contents.values()))
            content = section[0]
            return redirect('course_navigation_content', courseid=courseid, coursecontentid=content.id)

        coursecontent = get_object_or_404(CourseContent, id=coursecontentid)

        course_progress_count = CourseProgress.objects.filter(enrollment=enrollment, status=True).count()
        course_contents_count = CourseContent.objects.filter(section__course_id=enrollment.course.id).count()
        progress = 100
        if course_contents_count is not 0:
            progress = int((course_progress_count / course_contents_count) * 100)

        try:
            courseProgress = CourseProgress.objects.get(enrollment=enrollment, course_content=coursecontent)
        except CourseProgress.DoesNotExist:
            courseProgress = None
        context = {
            'user_profile': user_profile,
            'course': course,
            'contents': contents,
            'coursecontent': coursecontent,
            'courseProgress': courseProgress,
            'progress': progress,
        }
        return render(request, 'course_navigation.html', context)

    def post(self, request, courseid, coursecontentid):
        # user_profile = UserProfile.objects.get(user_id=request.user.id)
        enrollment = Enrollment.objects.get(student_id=request.user.id, course_id=courseid)

        course_content = get_object_or_404(CourseContent, id=coursecontentid)

        CourseProgress.objects.get_or_create(
            enrollment=enrollment,
            course_content=course_content,
            status=True,
        )
        return redirect('course_navigation_content', courseid=courseid, coursecontentid=coursecontentid)


@method_decorator(login_required, name="dispatch")
class CourseContentFileView(View):
    def get(self, request, coursecontentid):
        # Get the PDF file path based on the provided ID
        content = get_object_or_404(CourseContent, id=coursecontentid)
        pdf_file_path = os.path.join(settings.MEDIA_ROOT, str(content.filepath))
        # Check if the PDF file exists
        if os.path.exists(pdf_file_path):
            # Open the PDF file in binary mode
            pdf_file = open(pdf_file_path, 'rb')

            # Create the response with appropriate headers
            response = FileResponse(pdf_file, content_type='application/pdf')
            response['Content-Length'] = os.path.getsize(pdf_file_path)
            return response

        else:
            # Handle the case if the PDF file doesn't exist
            return HttpResponse("PDF file not found", status=404)


@method_decorator(login_required, name="dispatch")
class Payment(View):
    def get(self, request):
        print('Insdie payment view : GET')
        membership_selected = request.GET.get('membership_selected')
        user_profile = UserProfile.objects.get(user=request.user)
        existing_membership = user_profile.membership.name
        if (existing_membership == 'silver' and membership_selected == 'bronze') or (
                existing_membership == 'gold' and membership_selected == 'bronze') or (
                existing_membership == 'gold' and membership_selected == 'silver'):
            print("inside if condition ")
            user_profile.membership = Membership.objects.get(name=membership_selected)
            user_profile.save()
            response = redirect('profile')
            response.set_cookie('membership_selected', membership_selected, max_age=60)
            return response
        context = {
            'membership_selected': membership_selected,
            'existing_membership': existing_membership,
            'user_profile': user_profile,
            'today_date': date.today().isoformat()
        }
        response = render(request, 'payment.html', context)
        response.set_cookie('membership_selected', membership_selected, max_age=60)
        # response.set_cookie('existing_membership', existing_membership, max_age=60)
        # response.set_cookie('existing_membership', existing_membership, max_age=60)
        return response

    def post(self, request):
        print('Insdie payment view : POST')
        membership_name = request.COOKIES.get('membership_selected')
        print(f"existing_membership form cookie is : {membership_name}")
        if membership_name is None:
            membership_name = request.POST.get('membership_selected')
            print(f"existing_membership form POST is : {membership_name}")

        user_profile = get_object_or_404(UserProfile, user=request.user)

        user_profile.membership = Membership.objects.get(name=membership_name)
        user_profile.save()
        response = redirect('profile')
        response.set_cookie('membership_selected', membership_name, max_age=60)
        return response


@login_required
def download_certificate(request, courseid):
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    certificate = Certificate.objects.filter(student_id=request.user.id, course_id=courseid).first()
    course = Course.objects.get(pk=courseid)
    filepath = None
    if certificate:
        filepath = certificate.filepath
    pdf_file_path = os.path.join(settings.CERTIFICATE_PATH, str(filepath))
    if not os.path.exists(pdf_file_path) or not certificate:
        if certificate:
            certificate.delete()
        currentDate = datetime.now().strftime('%Y-%m-%d')
        randomGuid = str(uuid.uuid4())
        filepath = randomGuid + '.pdf'
        instructor_name = course.instructor.username
        pdf_file_path = os.path.join(settings.CERTIFICATE_PATH, str(filepath))
        if not PdfGen.generate_pdf(user_profile.user.username, currentDate, instructor_name, course.name,
                                   pdf_file_path):
            return HttpResponse("Interval Server Error", status=500)

        certificate = Certificate(
            student=request.user,
            course=course,
            issue_date=datetime.now(),
            filepath=filepath
        )
        certificate.save()

    pdf_file_path = os.path.join(settings.CERTIFICATE_PATH, str(filepath))

    # Check if the PDF file exists
    if os.path.exists(pdf_file_path):
        # Open the PDF file in binary mode
        pdf_file = open(pdf_file_path, 'rb')

        # Create the response with appropriate headers
        response = FileResponse(pdf_file, content_type='application/pdf')
        response['Content-Length'] = os.path.getsize(pdf_file_path)
        return response

    else:
        # Handle the case if the PDF file doesn't exist
        return HttpResponse("PDF file not found", status=404)
