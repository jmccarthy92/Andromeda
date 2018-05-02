from django.db import models
from django.contrib.auth.models import User
from .utils import ChoiceEnum
from django.core.validators import MaxValueValidator, MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
import datetime
YEAR_CHOICES = []
for r in range(1980, (datetime.datetime.now().year+1)):
    YEAR_CHOICES.append((r, r))

# TODO: add helper methods and models should be complete.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    USER_CHOICES = (
        ('A', 'A'),
        ('S', 'S'),
        ('F', 'F'),
        ('R', 'R')
    )

    user_type = models.CharField(max_length=1, choices=USER_CHOICES, blank=True)

    def has_student(self):
        has_student = False
        try:
            has_student = (self.student is not None)
        except Student.DoesNotExist:
            pass
        return has_student

    def has_admin(self):
        has_admin = False
        try:
            has_admin = (self.admin is not None)
        except Admin.DoesNotExist:
            pass
        return has_admin

    def has_researcher(self):
        has_researcher = False
        try:
            has_researcher = (self.researcher is not None)
        except Researcher.DoesNotExist:
            pass
        return has_researcher

    def has_faculty(self):
        has_faculty = False
        try:
            has_faculty = (self.faculty is not None)
        except Faculty.DoesNotExist:
            pass
        return has_faculty


class Admin(models.Model):
    admin_id = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def __str__(self):
        return '{}'.format(self.admin_id)


class Student(models.Model):
    student_id = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    date_of_birth = models.DateField()

    STUDENT_CHOICES = (
        ('F', 'F'),
        ('P', 'P')
    )

    student_type = models.CharField(max_length=1, choices=STUDENT_CHOICES)

    def __str__(self):
        return '{}'.format(self.student_id, self.date_of_birth, self.student_type)

    def has_full_time_student(self):
        has_ft = False
        try:
            has_ft = (self.fulltimestudent is not None)
        except FullTimeStudent.DoesNotExist:
            pass
        return has_ft

    def has_part_time_student(self):
        has_pt = False
        try:
            has_pt = (self.parttimestudent is not None)
        except PartTimeStudent.DoesNotExist:
            pass
        return has_pt

    def was_born_before_year(self, year):
        return self.date_of_birth < datetime.date(year, 1, 1)

    def was_born_after_year(self, year):
        return self.date_of_birth >= datetime.date(year, 1, 1)


class FullTimeStudent(models.Model):
    student_id = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    credits = models.IntegerField(default=0)

    def __str__(self):
        return '{} {}'.format(self.student_id, self.credits)

    def is_senior(self):
        return self.credits > 108


class PartTimeStudent(models.Model):
    student_id = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    credits = models.IntegerField(default=0)

    def __str__(self):
        return '{} {}'.format(self.student_id, self.credits)

    def is_senior(self):
        return self.credits > 108


class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    chair_id = models.OneToOneField(
        'Faculty',
        on_delete=models.CASCADE,
        null=True
    )
    name = models.CharField(max_length=100)
    phone_number = PhoneNumberField()
    building_id = models.ForeignKey(
        'Building',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return '{} {} {} {} {}'.format(self.department_id, self.chair_id, self.name,
                                       self.phone_number, self.building_id)


class Faculty(models.Model):
    faculty_id = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    department_id = models.ForeignKey('Department', on_delete=models.CASCADE)

    FACULTY_CHOICES = (
        ('P', 'P'),
        ('F', 'F')
    )

    faculty_type = models.CharField(max_length=1, choices=FACULTY_CHOICES)

    # def __str__(self):
    #     return '{} {} {}'.format(self.faculty_id, self.department_id, self.faculty_type)

    def has_full_time_faculty(self):
        has_ft = False
        try:
            has_ft = (self.fulltimefaculty is not None)
        except FullTimeFaculty.DoesNotExist:
            pass
        return has_ft

    def has_part_time_faculty(self):
        has_pt = False
        try:
            has_pt = (self.parttimefaculty is not None)
        except PartTimeFaculty.DoesNotExist:
            pass
        return has_pt


class FullTimeFaculty(models.Model):
    faculty_id = models.OneToOneField(
        Faculty,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def __str__(self):
        return '{}'.format(self.faculty_id)


class PartTimeFaculty(models.Model):
    faculty_id = models.OneToOneField(
        Faculty,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def __str__(self):
        return '{}'.format(self.faculty_id)


class Researcher(models.Model):
    researcher_id = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def __str__(self):
        return '{}'.format(self.researcher_id)


class Advising(models.Model):
    advising_id = models.AutoField(primary_key=True)
    faculty_id = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {}'.format(self.advising_id, self.faculty_id, self.student_id)

    class Meta:
        unique_together = ('faculty_id', 'student_id')


class Hold(models.Model):
    hold_id = models.AutoField(primary_key=True)

    HOLD_CHOICES = (
        ('ACADEMIC', 'ACADEMIC'),
        ('DISCIPLINARY', 'DISCIPLINARY'),
        ('FINANCIAL', 'FINANCIAL'),
        ('MEDICAL', 'MEDICAL')
    )

    name = models.CharField(max_length=100, choices=HOLD_CHOICES)

    def __str__(self):
        return '{} {}'.format(self.hold_id, self.name)


class StudentHold(models.Model):
    student_hold_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    hold_id = models.ForeignKey(Hold, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {}'.format(self.student_hold_id, self.student_id, self.hold_id)

    class Meta:
        unique_together = ('student_id', 'hold_id')


class Major(models.Model):
    major_id = models.AutoField(primary_key=True)
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=254)

    def __str__(self):
        return '{} {} {}'.format(self.major_id, self.department_id, self.name)


class StudentMajor(models.Model):
    student_major_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    major_id = models.ForeignKey(Major, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {}'.format(self.student_id, self.student_major_id, self.major_id)

    class Meta:
        unique_together = ('student_id', 'major_id')


class MajorRequirement(models.Model):
    major_req_id = models.AutoField(primary_key=True)
    major_id = models.ForeignKey(Major, on_delete=models.CASCADE)
    course_id = models.ForeignKey('Course', on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {}'.format(self.major_req_id, self.course_id, self.major_id)

    class Meta:
        unique_together = ('course_id', 'major_id')


class Minor(models.Model):
    minor_id = models.AutoField(primary_key=True)
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=254)

    def __str__(self):
        return '{} {} {}'.format(self.minor_id, self.department_id, self.name)


class StudentMinor(models.Model):
    student_minor_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    minor_id = models.ForeignKey(Minor, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {}'.format(self.student_id, self.student_minor_id, self.minor_id)

    class Meta:
        unique_together = ('student_id', 'minor_id')


class MinorRequirement(models.Model):
    minor_req_id = models.AutoField(primary_key=True)
    minor_id = models.ForeignKey(Minor, on_delete=models.CASCADE)
    course_id = models.ForeignKey('Course', on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {}'.format(self.minor_id, self.minor_req_id, self.course_id)

    class Meta:
        unique_together = ('course_id', 'minor_id')


class Meetings(models.Model):
    meeting_id = models.AutoField(primary_key=True)
    enrollment_id = models.ForeignKey('Enrollment', on_delete=models.CASCADE)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    meeting_date = models.DateField('meeting date', null=True)
    present_or_absent = models.BooleanField(default=False)
    # submitted = models.BooleanField(default=False)

    def __str__(self):
        return '{} {} {} {} {}'.format(self.meeting_id, self.enrollment_id, self.student_id, self.meeting_date,
                                       self.present_or_absent)

    class Meta:
        unique_together = ('enrollment_id', 'student_id')


class Prerequisite(models.Model):
    prerequisite_id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='prerequisite_course_id')
    course_required_id = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='course_required_id')

    def __str__(self):
        return '{} {} {}'.format(self.prerequisite_id, self.course_required_id, self.course_id)

    class Meta:
        unique_together = ('course_id', 'course_required_id')


class StudentHistory(models.Model):
    student_hist_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    enrollment_id = models.ForeignKey('Enrollment', on_delete=models.CASCADE)
    adviser = models.OneToOneField(
        Faculty,
        on_delete=models.CASCADE,
        null=True
    )

    STATUS_CHOICES = (
        ('FRESHMAN', 'FRESHMAN'),
        ('SOPHOMORE', 'SOPHOMORE'),
        ('JUNIOR', 'JUNIOR'),
        ('SENIOR', 'SENIOR'),
        ('GRADUATE', 'GRADUATE'),
        ('GRADUATE_STUDENT', 'GRADUATE_STUDENT')
    )

    status = models.CharField(max_length=35, choices=STATUS_CHOICES)

    def __str__(self):
        return '{} {} {} {} {}'.format(self.student_id, self.student_hist_id, self.enrollment_id,
                                       self.adviser, self.status)

    class Meta:
        unique_together = ('student_id', 'enrollment_id')


class Section(models.Model):
    section_id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey('Course', on_delete=models.CASCADE)
    faculty_id = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    time_slot_id = models.ForeignKey('TimeSlot', on_delete=models.CASCADE, null=True)
    seats_taken = models.IntegerField(default=0)
    semester_id = models.ForeignKey('Semester', on_delete=models.CASCADE, null=True)
    room_id = models.ForeignKey('Room', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return '{} {} {} {} {} {} {} '.format(self.section_id, self.course_id, self.faculty_id,
                                                self.time_slot_id,  self.seats_taken,
                                                self.semester_id, self.room_id)

    def seats_filled(self):
        return self.seat_capacity == self.seats_taken

    def is_offered_in_season(self, season):
        return self.semester_id.season == season

    class Meta:
        unique_together = ('section_id', 'course_id')


class Enrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    section_id = models.ForeignKey(Section, on_delete=models.CASCADE)

    GRADE_CHOICES = (
        ('A', 'A'),
        ('A-', 'A-'),
        ('B', 'B'),
        ('B-', 'B-'),
        ('C', 'C'),
        ('C-', 'C-'),
        ('D', 'D'),
        ('D-', 'D-'),
        ('F', 'F'),
        ('W', 'W'),
        ('I', 'I'),
        ('NA', 'NA')
    )

    grade = models.CharField(max_length=2, default='NA', choices=GRADE_CHOICES)

    def __str__(self):
        return '{} {} {}'.format(self.student_id, self.section_id, self.grade)

    def grade_c_or_above(self):
        return self.grade in ['A', 'A-', 'B', 'B-', 'C']

    class Meta:
        unique_together = ('student_id', 'section_id')


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)

    credits = models.IntegerField(default=3, validators=[ MaxValueValidator(4), MinValueValidator(2)])

    def __str__(self):
        return '{} {} {} {} {}'.format(self.course_id, self.department_id, self.name,
                                       self.description, self.credits)

    def has_prerequisites(self):
        try:
            Prerequisite.objects.get(course_id=self.course_id)
            return True
        except Prerequisite.DoesNotExist:
            return False


class Semester(models.Model):
    semester_id = models.AutoField(primary_key=True)
    year = models.IntegerField(choices=YEAR_CHOICES, default=datetime.datetime.now().year)

    SEMESTER_STATUS = (
        ('OPEN_GRADING', 'OPEN_GRADING'),
        ('CLOSE', 'CLOSE'),
        ('OPEN_REGISTRATION', 'OPEN_REGISTRATION')
    )

    SEASON_CHOICES = (
        ('WINTER', 'WINTER'),
        ('SPRING', 'SPRING'),
        ('FALL', 'FALL'),
        ('SUMMER', 'SUMMER')
    )
    status = models.CharField(max_length=35, default='CLOSE', choices=SEMESTER_STATUS)
    season = models.CharField(max_length=7, choices=SEASON_CHOICES)

    def __str__(self):
        return '{} {} {}'.format(self.semester_id, self.season, self.year)


class Building(models.Model):
    building_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    def __str__(self):
        return '{} {} {}'.format(self.building_id, self.name, self.address)


class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    building_id = models.ForeignKey(Building, on_delete=models.CASCADE)
    type = models.CharField(max_length=35)
    capacity = models.IntegerField()
    room_number = models.CharField(max_length=5)

    def room_cap_greater_than(self, value):
        return self.capacity > value

    def __str__(self):
        return '{} {} {} {} {}'.format(self.room_id, self.building_id, self.capacity,
                                       self.room_number, self.type)


class MeetingDays(models.Model):
    days_id = models.AutoField(primary_key=True)

    DAY_CHOICES = (
        ('MONDAY', 'MONDAY'),
        ('TUESDAY', 'TUESDAY'),
        ('WEDNESDAY', 'WEDNDESDAY'),
        ('THURSDAY', 'THURSDAY'),
        ('FRIDAY', 'FRIDAY'),
        ('SATURDAY', 'SATURDAY'),
        ('SUNDAY', 'SUNDAY')
    )

    day_1 = models.CharField(max_length=10, choices=DAY_CHOICES)
    day_2 = models.CharField(max_length=10, choices=DAY_CHOICES, null=True)
    day_3 = models.CharField(max_length=10, choices=DAY_CHOICES, null=True)

    def __str__(self):
        return '{} {} {}'.format(self.days_id, self.day_1, self.day_2)


class Period(models.Model):
    period_id = models.AutoField(primary_key=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return '{} {} {}'.format(self.period_id, self.start_time, self.end_time)


class TimeSlot(models.Model):
    time_slot_id = models.AutoField(primary_key=True)
    days_id = models.ForeignKey(MeetingDays, on_delete=models.CASCADE)
    period_id = models.ForeignKey(Period, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {}'.format(self.time_slot_id, self.days_id, self.period_id)

    class Meta:
        unique_together = ('days_id', 'period_id')
