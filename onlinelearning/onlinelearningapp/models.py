from django.contrib.auth.models import User
from django.db import models


class Membership(models.Model):
    name = models.CharField(max_length=30)

    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(max_length=30)

    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username


# TODO: add a field in Course for gold bronze silver
# TODO: add the section logic by creating a new model
# TODO: map the section to coursecontent model
'''
Course:
cid

Section:
sid1 cid order
sid2 cid order
sid3 cid order

CourseContent:
ccid1 sid1 link order type
ccid2 sid1 link order type
ccid3 sid1 link order type
'''


class Course(models.Model):
    name = models.CharField(max_length=100)

    description = models.TextField()

    instructor = models.ForeignKey(User, on_delete=models.CASCADE)

    published = models.BooleanField()

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    date_enrolled = models.DateTimeField(auto_now_add=True)

    progress = models.IntegerField()

    def __str__(self):
        return f'{self.student.username} - {self.course.name}'


# TODO: add a model for CourseProgress which keeps tracks of each individual course content completed or not
class CourseProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    # TODO: map it to couse content
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.BooleanField()

    def __str__(self):
        return f'{self.student.username} - {self.course.name}'


class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    date = models.DateField()

    status = models.BooleanField()

    def __str__(self):
        return f'{self.student.username} - {self.course.name} - {self.date}'


class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    issue_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student.username} - {self.course.name}'


class Payment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)

    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, null=True, blank=True)

    amount = models.DecimalField(max_digits=5, decimal_places=2)

    currency = models.CharField(max_length=3)

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student.username} - {self.date}'
