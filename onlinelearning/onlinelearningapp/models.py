from django.contrib.auth.models import User
from django.db import models


# TODO: PREREQ-- While creating data for Membership create in the order of MEMBERSHIP_TYPES make sure the id matches
#     MEMBERSHIP_TYPES = (
#         (1, 'gold', '3', 'CAD'),
#         (2, 'silver','1', 'CAD'),
#         (3, 'bronze','0', 'CAD'),
#     )
class Membership(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    currency = models.CharField(max_length=3)

    def __str__(self):
        return f"Name: {self.name}, Price: {self.price}, Currency: {self.currency}"


class Role(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return f"RoleName: {self.name}"


'''
superuser - username - admin, password - 1234
'''


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, default=3)

    def __str__(self):
        return f"Username: {self.user.username}, Role: {self.role.name}, Membership: {self.membership.name}"


'''
Course:
cid

Section:
sid1 cid order1
sid2 cid order2
sid3 cid order3

CourseContent:
ccid1 sid1 link order1 type
ccid2 sid1 link order2 type
ccid3 sid1 link order3 type
'''


class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    membership_level_required = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, default=3)

    def __str__(self):
        return f"CourseName: {self.name}, Published: {self.published}, Instructor: {self.instructor.username}, " \
               f"Membership Level Required: {self.membership_level_required.name}"


class Section(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    order = models.IntegerField()

    class Meta:
        unique_together = ('course', 'order',)

    def __str__(self):
        return f"SectionName: {self.name}, Course: {self.course.name}, Order: {self.order}"


class CourseContent(models.Model):
    CONTENT_TYPES = (
        ('pdf', 'PDF'),
        ('video', 'VIDEO'),
        ('txt', 'TEXT'),
    )

    def course_file_path(self, filename):
        return f'courses/{self.section.course.id}/section_{self.section.id}/{filename}'

    name = models.CharField(max_length=100)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    filepath = models.FileField(upload_to=course_file_path)
    order = models.IntegerField()
    content_type = models.CharField(max_length=5, choices=CONTENT_TYPES)

    class Meta:
        unique_together = ('section', 'order',)

    def __str__(self):
        return f"ContentName: {self.name}, Course: {self.section.course.name}, Section: {self.section.name}, " \
               f"Order: {self.order}, Filepath: {self.filepath}, Content Type:{self.content_type}"


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Student: {self.student.username}, Course: {self.course.name}'


class CourseProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    course_content = models.ForeignKey(CourseContent, on_delete=models.CASCADE)
    status = models.BooleanField()

    def __str__(self):
        return f'Student: {self.enrollment.student.username}, Course: {self.course_content.section.course.name},' \
               f' Content: {self.course_content.name}, Status:{self.status}'


class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f'Student: {self.student.username}, Course: {self.course.name}, Date: {self.date}'


class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    filepath = models.CharField(max_length=500)

    def __str__(self):
        return f'Student: {self.student.username}, Course: {self.course.name},Filepath:{self.filepath}'


class Payment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Student: {self.student.username}, Membership:{self.membership},Date: {self.date}'
