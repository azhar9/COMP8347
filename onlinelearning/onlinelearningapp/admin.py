from django.contrib import admin

from .models import Membership, Role, UserProfile, Course, Section, CourseContent, Enrollment, CourseProgress, \
    Attendance, Certificate, Payment

# Register your models here.
admin.site.register(Membership)
admin.site.register(Role)
admin.site.register(UserProfile)
admin.site.register(Course)
admin.site.register(Section)
admin.site.register(CourseContent)
admin.site.register(Enrollment)
admin.site.register(CourseProgress)
admin.site.register(Attendance)
admin.site.register(Certificate)
admin.site.register(Payment)
