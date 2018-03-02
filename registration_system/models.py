from django.db import models
from django.contrib.auth.models import User
from .utils import ChoiceEnum
from phonenumber_field.modelfields import PhoneNumberField
import datetime
YEAR_CHOICES = []
for r in range(1980, (datetime.datetime.now().year+1)):
    YEAR_CHOICES.append((r, r))

# TODO: add helper methods and models should be complete.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class UserType(ChoiceEnum):
        ADMIN = 'A'
        STUDENT = 'S'
        FACULTY = 'F'
        RESEARCHER = 'R'

    user_type = models.CharField(max_length=1, choices=UserType.choices())


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

    class StudentType(ChoiceEnum):
        FULL_TIME = 'F'
        PART_TIME = 'P'

    student_type = models.CharField(max_length=1, choices=StudentType.choices())

    def __str__(self):
        return '{}'.format(self.student_id, self.date_of_birth, self.student_type)


class FullTimeStudent(models.Model):
    student_id = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    credits = models.IntegerField(default=0)

    def __str__(self):
        return '{} {}'.format(self.student_id, self.credits)


class PartTimeStudent(models.Model):
    student_id = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    credits = models.IntegerField(default=0)

    def __str__(self):
        return '{} {}'.format(self.student_id, self.credits)


class Faculty(models.Model):
    faculty_id = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE)

    class FacultyType(ChoiceEnum):
        FULL_TIME = 'F'
        PART_TIME = 'P'

    faculty_type = models.CharField(max_length=1, choices=FacultyType.choices())

    def __str__(self):
        return '{} {} {}'.format(self.faculty_id, self.department_id, self.faculty_type)


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

    class HoldType(ChoiceEnum):
        ACADEMIC = 'ACADEMIC'
        DISCIPLINARY = 'DISCIPLINARY'
        FINANCIAL = 'FINANCIAL'
        MEDICAL = 'MEDICAL'

    name = models.CharField(max_length=100)

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
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)

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
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {}'.format(self.minor_id, self.minor_req_id, self.course_id)

    class Meta:
        unique_together = ('course_id', 'minor_id')


class Meetings(models.Model):
    meeting_id = models.AutoField(primary_key=True)
    enrollment_id = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    meeting_date = models.DateTimeField('meeting date')
    present_or_absent = models.BooleanField(default=False)

    def __str__(self):
        return '{} {} {} {} {}'.format(self.meeting_id, self.enrollment_id, self.student_id
                                       , self.meeting_date, self.present_or_absent)

    class Meta:
        unique_together = ('enrollment_id', 'student_id')


class Prerequisite(models.Model):
    prerequisite_id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_required_id = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {}'.format(self.prerequisite_id, self.course_required_id, self.course_id)

    class Meta:
        unique_together = ('course_id', 'course_required_id')


class StudentHistory(models.Model):
    student_hist_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    enrollment_id = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    adviser = models.OneToOneField(
        Faculty,
        on_delete=models.CASCADE,
        null=True
    )

    class StatusType(ChoiceEnum):
        FRESHMAN = 'FRESHMAN'
        SOPHOMORE = 'SOPHOMORE'
        JUNIOR = 'JUNIOR'
        SENIOR = 'SENIOR'
        GRADUATED = 'GRADUATE'
        GRADUATE_STUDENT = 'GRADUATE_STUDENT'

    status = models.CharField(max_length=35, choices=StatusType)

    def __str__(self):
        return '{} {} {} {} {}'.format(self.student_id, self.student_hist_id, self.enrollment_id,
                                       self.adviser, self.status)

    class Meta:
        unique_together = ('student_id', 'enrollment_id')


class Section(models.Model):
    section_id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    faculty_id = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    time_slot_id = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, null=True)
    seat_capacity = models.IntegerField()
    seats_taken = models.IntegerField(default=0)
    semester_id = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return '{} {} {} {} {} {} {} {}'.format(self.section_id, self.course_id, self.faculty_id,
                                                self.time_slot_id, self.seat_capacity, self.seats_taken,
                                                self.semester_id, self.room_id)

    class Meta:
        unique_together = ('section_id', 'course_id')


class Enrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    section_id = models.ForeignKey(Section, on_delete=models.CASCADE)

    class GradeType(ChoiceEnum):
        A = 'A'
        A_minus = 'A-'
        B = 'B'
        B_minus = 'B-'
        C = 'C'
        C_minus = 'C-'
        D = 'D'
        D_minus = 'D-'
        F = 'F'
        Incomplete = 'I'
        Withdraw = 'W'
        NA = 'NA'

    grade = models.CharField(max_length=2, default='NA', choices=GradeType)

    def __str__(self):
        return '{} {} {} P{'.format(self.student_id, self.section_id, self.enrollment_id, self.grade)

    class Meta:
        unique_together = ('student_id', 'section_id')


class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    chair_id = models.OneToOneField(
        Faculty,
        on_delete=models.CASCADE,
        null=True
    )
    name = models.CharField(max_length=100)
    phone_number = PhoneNumberField()
    building_id = models.OneToOneField(
        Building,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return '{} {} {} {} {}'.format(self.department_id, self.chair_id, self.name,
                                       self.phone_number, self.building_id)


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    credits = models.IntegerField()

    def __str__(self):
        return '{} {} {} {} {}'.format(self.course_id, self.department_id, self.name,
                                       self.description, self.credits)


class Semester(models.Model):
    semester_id = models.AutoField(primary_key=True)
    year = models.IntegerField(choices=YEAR_CHOICES, default=datetime.datetime.now().year)

    class SeasonType(ChoiceEnum):
        WINTER = 'WINTER'
        SPRING = 'SPRING'
        FALL = 'FALL'
        SUMMER = 'SUMMER'

    season = models.CharField(max_length=7, choices=SeasonType)

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

    def __str__(self):
        return '{} {} {} {} {}'.format(self.room_id, self.building_id, self.capacity,
                                       self.room_number, self.type)


class MeetingDays(models.Model):
    days_id = models.AutoField(primary_key=True)

    class DayType(ChoiceEnum):
        MONDAY = 'MONDAY'
        TUESDAY = 'TUESDAY'
        WEDNESDAY = 'WEDNESDAY'
        THURSDAY = 'THURSDAY'
        FRIDAY = 'FRIDAY'
        SATURDAY = 'SATURDAY'
        SUNDAY = 'SUNDAY'

    day_1 = models.CharField(max_length=10, choices=DayType)
    day_2 = models.CharField(max_length=10, choices=DayType)

    def __str__(self):
        return '{} {} {}'.format(self.days_id, self.day_1, self.day_2)


class Period(models.Model):
    period_id = models.AutoField(primary_key=True)
    start_time = models.TimeField(input_formats="%H:%i")
    end_time = models.TimeField(input_formats="%H:%i")

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
