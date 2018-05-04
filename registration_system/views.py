import os, json, csv
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from react.render import render_component
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from .models import *
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import *
from django.views import generic
from datetime import datetime


# Instead of using signals in views to create child models
# Just create the Instance of the parent class and an instance of the child class
# point the child's foreign key reference to the parent class. have to fo for Faculty and Student models


# Create your views here.
# @login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/student_system/")


def home(request):
    # return render(request, 'registration_system/index.html')
    rendered = render_component(
        os.path.join(os.getcwd(), 'registration_system', 'static', 'registration_system', 'js', 'intro-page.jsx'),
        {
            'test': 'REALLY LONG full test',
        },
        to_static_markup=False,
    )
    print(request.user)
    if request.user:
        user = request.user
    else:
        user = False
    # print(rendered)
    return render(request, 'registration_system/index.html', {'rendered': rendered, 'user': user})


class AppointChair(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/appoint_chair.html'
    is_admin = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)
        if userprofile:
            if userprofile.has_admin():
                self.is_admin = True
            else:
                return redirect('/student_system/')

        departments = Department.objects.all()

        if request.is_ajax():
            department_id = request.GET.get('department_id')
            faculty = Faculty.objects.filter(department_id_id=int(department_id))
            faculty_array = []
            print(faculty)
            for f in faculty:
                data = {
                    'faculty_name': f.faculty_id.user.first_name + ' ' + f.faculty_id.user.last_name,
                    'faculty_id': f.faculty_id_id
                }
                faculty_array.append(data)
            return HttpResponse(json.dumps(faculty_array), content_type="application/json")

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_admin': self.is_admin,
                'header_text': 'Appoint Chairperson'
            },
            to_static_markup=False,
        )
        return render(request, self.template_name, {'rendered': rendered, 'departments': departments})

    def post(self, request, *args, **kwargs):
        data = {
            'is_successful': False
        }
        if request.is_ajax():
            department_id = request.POST.get('department_id')
            faculty_id = request.POST.get('faculty_id')
            print(department_id)
            print(faculty_id)
            faculty = Faculty.objects.get(pk=int(faculty_id))
            # = request.POST.get('hold')
            department = Department.objects.get(pk=int(department_id))
            department.chair_id = faculty
            department.save()
            data['is_successful'] = True
        else:
            data['is_successful'] = False
        return JsonResponse(data)


class CreateReport(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/create_report.html'
    is_researcher = False
    grading_key = {
        'A': 4.0,
        'A-': 3.5,
        'B': 3.0,
        'B-': 2.5,
        'C': 2.0,
        'C-': 1.5,
        'D': 1.0,
        'D-': 0.5,
        'F': 0
    }

    def get(self, request, *args, **kwargs):
        user = request.user
        user_profile = UserProfile.objects.get(user=user)

        if user_profile:
            if user_profile.has_researcher():
                self.is_researcher = True
            else:
                return redirect('/student_system/')

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_researcher': self.is_researcher,
                'header_text': 'Generate Report '
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered,
        }

        return render(request, self.template_name, context)


class ViewGraphs(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/view_graphs.html'
    is_researcher = False
    grading_key = {
        'A': 4.0,
        'A-': 3.5,
        'B': 3.0,
        'B-': 2.5,
        'C': 2.0,
        'C-': 1.5,
        'D': 1.0,
        'D-': 0.5,
        'F': 0
    }

    def get(self, request, *args, **kwargs):
        user = request.user
        user_profile = UserProfile.objects.get(user=user)

        if user_profile:
            if user_profile.has_researcher():
                self.is_researcher = True
            else:
                return redirect('/student_system/')

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_researcher': self.is_researcher,
                'header_text': 'View Graphs '
            },
            to_static_markup=False,
        )
        grades_tally = [0] * 9
        grades = [4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0, 0.5, 0]
        grades = ['A', 'A-', 'B', 'B-', 'C', 'C-', 'D', 'D-', 'F']
        for e in Enrollment.objects.all():
            if e.grade == 'A':
                grades_tally[0] = grades_tally[0] + 1
            elif e.grade == 'A-':
                grades_tally[1] = grades_tally[1] + 1
            elif e.grade == 'B':
                grades_tally[2] = grades_tally[2] + 1
            elif e.grade == 'B-':
                grades_tally[3] = grades_tally[3] + 1
            elif e.grade == 'C':
                grades_tally[4] = grades_tally[4] + 1
            elif e.grade == 'C-':
                grades_tally[5] = grades_tally[5] + 1
            elif e.grade == 'D':
                grades_tally[6] = grades_tally[6] + 1
            elif e.grade == 'D-':
                grades_tally[7] = grades_tally[7] + 1
            elif e.grade == 'F':
                grades_tally[8] = grades_tally[8] + 1

        course_name = {}
        for c in Course.objects.all():
            course_name[c.name] = {
                'tally': 0
            }

        for s in Section.objects.all():
            course_name[s.course_id.name]['tally'] = course_name[s.course_id.name]['tally'] + s.seats_taken
        # meeting_dates = {}
        # for m in Meetings.objects.values('meeting_date').distinct():
        #     # print(m)
        #     meeting_dates[m['meeting_date'].strftime("%Y-%m-%d")] = {
        #         'date': m['meeting_date'].strftime("%Y-%m-%d"),
        #         'tally': 0
        #     }
        # for m in Meetings.objects.all():
        #     if m.meeting_date.strftime("%Y-%m-%d") == meeting_dates[m.meeting_date.strftime("%Y-%m-%d")]['date']:
        #         meeting_dates[m.meeting_date.strftime("%Y-%m-%d")]['tally'] = meeting_dates[m.meeting_date.strftime("%Y-%m-%d")]['tally'] + 1
        # print(meeting_dates)
        meeting_date_x_axis = []
        meeting_date_y_axis = []
        # for key, value in meeting_dates.items():
        #     meeting_date_x_axis.append(value['date'])
        #     meeting_date_y_axis.append(value['tally'])
        for key, value in course_name.items():
            meeting_date_x_axis.append(key)
            meeting_date_y_axis.append(value['tally'])
        context = {
            'rendered': rendered,
            'x_axis': grades,
            'y_axis': grades_tally,
            'meeting_dates_x_axis': meeting_date_x_axis,
            'meeting_dates_y_axis': meeting_date_y_axis
        }

        return render(request, self.template_name, context)


class AttendanceSubmitted(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/attendance_submitted.html'
    is_faculty = False

    def get(self, request, section_id, *args, **kwargs):
        user = request.user
        user_profile = UserProfile.objects.get(user=user)

        if user_profile:
            if user_profile.has_faculty():
                self.is_faculty = True
            else:
                return redirect('/student_system/')

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_faculty': self.is_faculty,
                'header_text': 'Attendance Submitted: '
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered,
            'section': Section.objects.get(pk=int(section_id)),
            'todays_date': datetime.today
        }

        return render(request, self.template_name, context)


class ViewAttendance(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/view_attendance.html'
    is_faculty = False

    def get(self, request, *args, **kwargs):
        user = request.user
        user_profile = UserProfile.objects.get(user=user)

        if user_profile:
            if user_profile.has_faculty():
                self.is_faculty = True
            else:
                return redirect('/student_system/')

        if request.is_ajax():
            section_id = request.GET.get('section_id')
            meeting_date = request.GET.get('meeting_date')
            meeting_date = datetime.fromtimestamp(float(meeting_date) / 1000.0)
            print(meeting_date)
            meeting = Meetings.objects.filter(meeting_date=meeting_date, enrollment_id__section_id=section_id)
            meeting_array = []
            for m in meeting:
                meeting_array.append({
                    'meeting_id': m.meeting_id,
                    'student_id': m.student_id_id,
                    'first_name': m.student_id.student_id.user.first_name,
                    'last_name': m.student_id.student_id.user.last_name,
                    'meeting_date': m.meeting_date.strftime("%Y-%m-%d"),
                    'present_or_absent': m.present_or_absent
                })

            data = {
                'meeting_array': meeting_array
            }
            return HttpResponse(json.dumps(data), content_type="application/json")

        sections = Section.objects.filter(faculty_id=user_profile.faculty)
        meetings = Meetings.objects.raw("SELECT distinct meeting_id, meeting_date, section_id_id "
                                        "from registration_system_meetings, registration_system_enrollment, "
                                            "registration_system_section "
                                        "where registration_system_meetings.enrollment_id_id = registration_system_enrollment.enrollment_id")

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static', 'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_faculty': self.is_faculty,
                'header_text': 'View Attendance'
            },
            to_static_markup=False,
        )
        context = {
            'rendered': rendered,
            'meetings': meetings,
            'sections': sections,
            'todays_date': datetime.today
        }

        return render(request, self.template_name, context)


class TakeAttendance(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/take_attendance.html'
    is_faculty = False

    def get(self, request, *args, **kwargs):
        user = request.user
        user_profile = UserProfile.objects.get(user=user)

        if user_profile:
            if user_profile.has_faculty():
                self.is_faculty = True
            else:
                return redirect('/student_system/')

        if request.is_ajax():
            section_id = request.GET.get('section_id')
            closest_date = request.GET.get('closest_date')
            closest_date = datetime.fromtimestamp(float(closest_date) / 1000.0)

            meetings = Meetings.objects.filter(meeting_date=closest_date)

            # except Meetings.DoesNotExist:
            if not meetings:
                enrollment = Enrollment.objects.filter(section_id_id=int(section_id))
                # enrollments = Enrollment.objects.filter(section_id=section_id)
                section = Section.objects.get(pk=int(section_id))
                section_name = section.course_id.name
                students_array = []
                for m in enrollment:
                    students_array.append({
                        # 'section_id': e.section_id_id,
                        'enrollment_id': m.enrollment_id,
                        'student_id': m.student_id_id,
                        'first_name': m.student_id.student_id.user.first_name,
                        'last_name': m.student_id.student_id.user.last_name,
                        # 'present_or_absent': m.present_or_absent
                    })
                data = {
                    'students_array': students_array,
                    'section_name': section_name,
                    'meeting_day_1': section.time_slot_id.days_id.day_1,
                    'meeting_day_2': section.time_slot_id.days_id.day_2,
                    'section_id': section_id,
                    'semester_status': Section.objects.get(pk=int(section_id)).semester_id.status
                }

                return HttpResponse(json.dumps(data), content_type="application/json")
            else:
                data = {
                    'meeting_submitted': True
                }
                return HttpResponse(json.dumps(data), content_type='application/json')

        sections = Section.objects.filter(faculty_id=user_profile.faculty)
        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_faculty': self.is_faculty,
                'header_text': 'Take Section Attendance'
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered,
            'sections': sections,
            'todays_date': datetime.today
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = {
            'is_successful': False
        }
        if request.is_ajax():
            student_array_data = request.POST.get('students_array')
            attendance_date_in = request.POST.get('attendance_date')
            student_array = json.loads(student_array_data)
            print(attendance_date_in)
            attendance_date = datetime.fromtimestamp(float(attendance_date_in)/1000.0)
            # attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
            print(student_array)
            print(attendance_date)
            for s in student_array:
                meetings = Meetings.objects.create(enrollment_id=Enrollment.objects.get(pk=int(s['enrollment_id'])),
                                                   student_id=Student.objects.get(pk=int(s['student_id'])),
                                                   present_or_absent=s['is_checked'],
                                                   meeting_date=attendance_date)
            # present_or_absent = request.POST.get('present_or_absent_id')
            # meetings = Meetings.objects.get(enrollment_id=enrollment_id, student_id=student_id)
            # if present_or_absent == 'P':
            #     meetings.present_or_absent = True
            # else:
            #     meetings.present_or_absent = False
            # meetings.meeting_date = datetime.today
            # meetings.save()
            data['is_successful'] = True
            return JsonResponse(data)


class SubmitGrades(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/submit_grades.html'
    is_faculty = False

    def get(self, request, *args, **kwargs):
        user = request.user
        user_profile = UserProfile.objects.get(user=user)

        if user_profile:
            if user_profile.has_faculty():
                self.is_faculty = True
            else:
                return redirect('/student_system/')

        if request.is_ajax():
            section_id = request.GET.get('section_id')
            enrollments = Enrollment.objects.filter(section_id=section_id)
            section_name = Section.objects.get(pk=int(section_id)).course_id.name
            students_array = []
            for e in enrollments:

                students_array.append({
                    # 'section_id': e.section_id_id,
                    'student_id': e.student_id_id,
                    'first_name': e.student_id.student_id.user.first_name,
                    'last_name': e.student_id.student_id.user.last_name
                })
            data = {
                'students_array': students_array,
                'section_name': section_name,
                'section_id': section_id,
                'semester_status': Section.objects.get(pk=int(section_id)).semester_id.status
            }

            return HttpResponse(json.dumps(data), content_type="application/json")

        sections = Section.objects.filter(faculty_id=user_profile.faculty)

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                             'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_faculty': self.is_faculty,
                'header_text': 'Grading'
            },
            to_static_markup=False,
            )

        context = {
            'rendered': rendered,
            'sections': sections,
            'semesters': Semester.objects.all()
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = {
            'is_successful': False
        }
        if request.is_ajax():
            student_id = request.POST.get('student_id')
            section_id = request.POST.get('section_id')
            letter_grade = request.POST.get('letter_grade')
            enrollment = Enrollment.objects.get(section_id=section_id, student_id=student_id)
            enrollment.grade = letter_grade
            enrollment.save()
            data['is_successful'] = True
        else:
            data['is_successful'] = False
        return JsonResponse(data)


class ViewFacultySchedule(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/view_faculty_schedule.html'
    is_faculty = True

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)
        if userprofile and userprofile.has_faculty():
            self.is_faculty = True
        else:
            return redirect('/student_system/')

        if request.is_ajax():
            semester_id = request.GET.get('semester_id')
            sections_array = []
            for e in Section.objects.filter(faculty_id=userprofile.faculty,
                                            semester_id_id=int(semester_id)).order_by('time_slot_id'):
                prerequisites = Prerequisite.objects.filter(course_id=e.course_id)
                prereq_array = []
                for p in prerequisites:
                    prereq_array.append({
                        'name': p.course_required_id.name
                    })
                faculty_name = e.faculty_id.faculty_id.user.first_name + " " + e.faculty_id.faculty_id.user.last_name
                sections_array.append({
                    'section_id': e.section_id,
                    'course_name': e.course_id.name,
                    'professor': faculty_name,
                    'credits': e.course_id.credits,
                    'room_number': e.room_id.room_number,
                    'building': e.room_id.building_id.name,
                    'meeting_days': e.time_slot_id.days_id.day_1 + " " + e.time_slot_id.days_id.day_2,
                    'time_period': e.time_slot_id.period_id.start_time.strftime('%H:%M %p') + "-"
                                   + e.time_slot_id.period_id.end_time.strftime('%H:%M %p'),
                    'seats_taken': e.seats_taken,
                    'seating_capacity': e.room_id.capacity,
                    'prerequisites': prereq_array
                })

            data = {
                'sections_array': sections_array,
                'faculty_name': user.first_name + " " + user.last_name,
                'is_successful': True
            }
            return HttpResponse(json.dumps(data), content_type="application/json")

        sections = Section.objects.filter(faculty_id=userprofile.faculty)
        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_faculty': self.is_faculty,
                'header_text': 'View Faculty Schedule'
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered,
            'sections': sections,
            'semesters': Semester.objects.all()
        }

        return render(request, self.template_name, context)


class ViewStudentSchedule(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/view_student_schedule.html'
    is_faculty = False
    is_admin = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)
        if userprofile and userprofile.has_faculty():
            self.is_faculty = True
        elif userprofile and userprofile.has_admin():
            self.is_admin = True
        else:
            return redirect('/student_system/')

        # print(self.is_faculty)
        current_user = userprofile.admin if self.is_admin else userprofile.faculty

        first_name = request.GET.get('first_name')
        last_name = request.GET.get('last_name')
        email = request.GET.get('email')
        username = request.GET.get('username')
        # user = User.objects.filter(Q(username=username) | Q(email=email) | Q(first_name=first_name) |
        #                            Q(last_name=last_name))
        if request.is_ajax():
            if username:
                user = User.objects.get(username=username)
            elif email:
                user = User.objects.get(email=email)
            elif first_name or last_name:
                user = User.objects.get(first_name=first_name, last_name=last_name)

            if user.userprofile.has_student():
                enrollment = Enrollment.objects.filter(student_id_id=user.userprofile.student.student_id_id)
                sections_array = []
                for e in enrollment:
                    prerequisites = Prerequisite.objects.filter(course_id=e.section_id.course_id)
                    prereq_array = []
                    for p in prerequisites:
                        prereq_array.append({
                            'name': p.course_required_id.name
                        })
                    faculty_name = e.section_id.faculty_id.faculty_id.user.first_name + " " + e.section_id.faculty_id.faculty_id.user.last_name
                    sections_array.append({
                        'section_id': e.section_id_id,
                        'course_department': e.section_id.course_id.department_id.name,
                        'course_name': e.section_id.course_id.name,
                        'professor': faculty_name,
                        'semester': e.section_id.semester_id.season + '-' + str(e.section_id.semester_id.year) + '--' + e.section_id.semester_id.status,
                        'credits': e.section_id.course_id.credits,
                        'room_number': e.section_id.room_id.room_number,
                        'building': e.section_id.room_id.building_id.name,
                        'meeting_days': e.section_id.time_slot_id.days_id.day_1 + " " + e.section_id.time_slot_id.days_id.day_2,
                        'time_period': e.section_id.time_slot_id.period_id.start_time.strftime('%H:%M %p') + "-"
                                       + e.section_id.time_slot_id.period_id.end_time.strftime('%H:%M %p'),
                        'seats_taken': e.section_id.seats_taken,
                        'seating_capacity': e.section_id.room_id.capacity,
                        'prerequisites': prereq_array
                    })
                data = {
                    'sections_array': sections_array,
                    'student_name': user.first_name + " " + user.last_name,
                    'is_successful': True
                }
                return HttpResponse(json.dumps(data), content_type="application/json")
            else:
                return HttpResponse(json.dumps({'is_successful': False}))

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                             'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_admin': self.is_admin,
                'is_faculty': self.is_faculty,
                'header_text': 'View Student Schedule'
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered
        }

        return render(request, self.template_name, context)


class StudentViewSchedule(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/student_view_student_schedule.html'
    is_student = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_student():
                self.is_student = True
            else:
                return redirect('/student_system/')

        if request.is_ajax():
                semester_id = request.GET.get('semester_id')
                sections_array = []
                for e in Enrollment.objects.filter(student_id=userprofile.student, section_id__semester_id__semester_id=int(semester_id)):
                    prerequisites = Prerequisite.objects.filter(course_id=e.section_id.course_id)
                    prereq_array = []
                    for p in prerequisites:
                        prereq_array.append({
                            'name': p.course_required_id.name
                        })
                    faculty_name = e.section_id.faculty_id.faculty_id.user.first_name + " " + e.section_id.faculty_id.faculty_id.user.last_name
                    sections_array.append({
                        'section_id': e.section_id_id,
                        'course_name': e.section_id.course_id.name,
                        'professor': faculty_name,
                        'credits': e.section_id.course_id.credits,
                        'room_number': e.section_id.room_id.room_number,
                        'building': e.section_id.room_id.building_id.name,
                        'meeting_days': e.section_id.time_slot_id.days_id.day_1 + " " + e.section_id.time_slot_id.days_id.day_2,
                        'time_period': e.section_id.time_slot_id.period_id.start_time.strftime('%H:%M %p') + "-"
                                       + e.section_id.time_slot_id.period_id.end_time.strftime('%H:%M %p'),
                        'seats_taken': e.section_id.seats_taken,
                        'seating_capacity': e.section_id.room_id.capacity,
                        'prerequisites': prereq_array
                    })

                data = {
                    'sections_array': sections_array,
                    'student_name': user.first_name + " " + user.last_name,
                    'is_successful': True
                }
                return HttpResponse(json.dumps(data), content_type="application/json")

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_student': self.is_student,
                'header_text': 'Student Schedule'
            },
            to_static_markup=False,
        )

        context = {
            'semesters': Semester.objects.all(),
            'rendered': rendered,
        }
        return render(request, self.template_name, context)


class ViewStudentTranscriptResult(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/view_student_transcript_result.html'
    is_faculty = False
    is_admin = False
    grading_key = {
        'A': 4.0,
        'A-': 3.5,
        'B': 3.0,
        'B-': 2.5,
        'C': 2.0,
        'C-': 1.5,
        'D': 1.0,
        'D-': 0.5,
        'F': 0
    }

    def get(self, request, student_id, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)
        if userprofile and userprofile.has_faculty():
            self.is_faculty = True
        elif userprofile and userprofile.has_admin():
            self.is_admin = True
        else:
            return redirect('/student_system/')
        student = Student.objects.get(pk=int(student_id))
        enrollments = Enrollment.objects.filter(student_id=student)
        enrollments_array = []
        grades = 0.0
        counter = 0
        # print(enrollments)
        try:
            student_major_rec = StudentMajor.objects.get(student_id=student)
            student_major = student_major_rec.major_id.name
            student_major_dep = student_major_rec.major_id.department_id.name
        except StudentMajor.DoesNotExist:
            student_major = 'None Declared'
            student_major_dep = 'N/A'

        adviser_array = []
        for a in Advising.objects.filter(student_id=student):
            adviser_array.append({
                'adviser_name': a.faculty_id.faculty_id.user.first_name + ' ' + a.faculty_id.faculty_id.user.last_name
            })
        for e in enrollments:
            if e.grade != 'I' and e.grade != 'W' and e.grade != 'NA':
                grades += self.grading_key[e.grade]

            counter = counter + 1
            enrollments_array.append({
                'course_name': e.section_id.course_id.name,
                'credits': e.section_id.course_id.credits,
                'semester_status': e.section_id.semester_id.status,
                'season': e.section_id.semester_id.season,
                'year': e.section_id.semester_id.year,
                'grade': e.grade
            })
        if counter == 0 and grades == 0.0:
            cumulative_gpa = 0.0
        else:
            cumulative_gpa = float(grades / counter)
        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_admin': self.is_admin,
                'is_faculty': self.is_faculty,
                'header_text': student.student_id.user.first_name+' '+student.student_id.user.last_name+'Transcript'
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered,
            'enrollment_array': enrollments_array,
            'cumulative_gpa': cumulative_gpa,
            'student_name': student.student_id.user.first_name + ' ' + student.student_id.user.last_name,
            'birth_date': student.date_of_birth.strftime("%Y-%m-%d"),
            'student_advisers': adviser_array,
            'major_and_department': student_major + " / " + student_major_dep
        }

        return render(request, self.template_name, context)


class ViewStudentTranscript(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/view_student_transcript.html'
    is_faculty = False
    is_admin = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)
        if userprofile and userprofile.has_faculty():
            self.is_faculty = True
        elif userprofile and userprofile.has_admin():
            self.is_admin = True
        else:
            return redirect('/student_system/')

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_admin': self.is_admin,
                'is_faculty': self.is_faculty,
                'header_text': 'View Transcript'
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        email = request.POST.get('email')
        # print(request.POST)

        if username:
            user = User.objects.get(username=username)
        elif email:
            user = User.objects.get(email=email)
        else:
            user = False

        userprofile = UserProfile.objects.get(user=user)
        if userprofile.has_student():
            student = userprofile.student
            return redirect('view_student_transcript_result', student_id=student.student_id_id)
        return redirect('/student_system/view_student_transcript/')


class StudentViewStudentTranscript(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/student_view_student_transcript.html'
    is_student = False
    grading_key = {
        'A': 4.0,
        'A-': 3.5,
        'B': 3.0,
        'B-': 2.5,
        'C': 2.0,
        'C-': 1.5,
        'D': 1.0,
        'D-': 0.5,
        'F': 0
    }

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_student():
                self.is_student = True
            else:
                return redirect('/student_system/')

        try:
            student_major_rec = StudentMajor.objects.get(student_id=userprofile.student)
            student_major = student_major_rec.major_id.name
            student_major_dep = student_major_rec.major_id.department_id.name
        except StudentMajor.DoesNotExist:
            student_major = 'None Declared'
            student_major_dep = 'N/A'
        adviser_array = []
        for a in Advising.objects.filter(student_id=userprofile.student):
            adviser_array.append({
                'adviser_name': a.faculty_id.faculty_id.user.first_name + ' ' + a.faculty_id.faculty_id.user.last_name
            })

        enrollments = Enrollment.objects.filter(student_id=userprofile.student)
        enrollments_array = []
        grades = 0.0
        counter = 0
        for e in enrollments:
            if e.grade != 'I' and e.grade != 'W' and e.grade != 'NA':
                grades += self.grading_key[e.grade]

            counter = counter + 1
            enrollments_array.append({
                'course_name': e.section_id.course_id.name,
                'credits': e.section_id.course_id.credits,
                'semester_status': e.section_id.semester_id.status,
                'season': e.section_id.semester_id.season,
                'year': e.section_id.semester_id.year,
                'grade': e.grade
            })
        if grades == 0.0 and counter == 0:
            cumulative_gpa = 0.0
        else:
            cumulative_gpa = float(grades/counter)

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_student': self.is_student,
                'header_text': 'View Transcript'
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered,
            'student_name': userprofile.user.first_name + '' + userprofile.user.last_name,
            'enrollment_array': enrollments_array,
            'birth_date': userprofile.student.date_of_birth.strftime("%Y-%m-%d"),
            'cumulative_gpa': cumulative_gpa,
            'student_advisers': adviser_array,
            'major_and_department': student_major + ' / ' + student_major_dep
        }

        return render(request, self.template_name, context)


# TODO: TEST
class DeclareMajor(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/declare_major.html'
    is_student = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_student():
                self.is_student = True
            else:
                return redirect('/student_system/')

        majors = Major.objects.all()
        has_major = True
        try:
            student = Student.objects.get(pk=int(user.userprofile.student.student_id_id))
            student_major = StudentMajor.objects.get(student_id=student).major_id.name
        except StudentMajor.DoesNotExist:
            has_major = False
            student_major = False

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_student': self.is_student,
                'header_text': 'Declare Major'
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered,
            'majors': majors,
            'student_major': student_major
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = {
            'is_successful': False
        }
        if request.is_ajax():
            user = request.user
            userprofile = UserProfile.objects.get(user=user)
            student = Student.objects.get(pk=userprofile.student.student_id_id)
            major_id = request.POST.get('major_id')
            major = Major.objects.get(pk=int(major_id))
            StudentMajor.objects.create(student_id=student, major_id=major)
            data['is_successful'] = True
        else:
            data['is_successful'] = False
        return JsonResponse(data)


# TODO: TEST
class DeclareMinor(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/declare_minor.html'
    is_student = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_student():
                self.is_student = True
            else:
                return redirect('/student_system/')

        minors = Minor.objects.all()

        try:
            student = Student.objects.get(pk=int(user.userprofile.student.student_id_id))
            student_minor = StudentMinor.objects.filter(student_id=student)
            student_minors = []
            for sm in student_minor:
                student_minors.append({
                    'name': sm.minor_id.name
                })
        except StudentMinor.DoesNotExist:
            student_minor = False

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_student': self.is_student,
                'header_text': 'Declare Minor'
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered,
            'minors': minors,
            'student_minors': student_minors
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = {
            'is_successful': False
        }
        if request.is_ajax():
            user = request.user
            userprofile = UserProfile.objects.get(user=user)
            student = Student.objects.get(pk=userprofile.student.student_id_id)
            minor_id = request.POST.get('minor_id')
            minor = Minor.objects.get(pk=int(minor_id))
            StudentMinor.objects.create(student_id=student, minor_id=minor)
            data['is_successful'] = True
        else:
            data['is_successful'] = False
        return JsonResponse(data)


class DropCourse(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/update_course.html'
    is_student = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_student():
                self.is_student = True
            else:
                return redirect('/student_system/')

        student = userprofile.student
        enrollment = Enrollment.objects.filter(student_id=student, section_id__semester_id__status='OPEN_REGISTRATION')
        sections_array = []
        for e in enrollment:
            prerequisites = Prerequisite.objects.filter(course_id=e.section_id.course_id)
            prereq_array = []
            for p in prerequisites:
                prereq_array.append({
                    'name': p.course_required_id.name
                })
            faculty_name = e.section_id.faculty_id.faculty_id.user.first_name + " " + e.section_id.faculty_id.faculty_id.user.last_name
            sections_array.append({
                'section_id': e.section_id_id,
                'course_name': e.section_id.course_id.name,
                'professor': faculty_name,
                'credits': e.section_id.course_id.credits,
                'room_number': e.section_id.room_id.room_number,
                'building': e.section_id.room_id.building_id.name,
                'meeting_days': e.section_id.time_slot_id.days_id.day_1 + " " + e.section_id.time_slot_id.days_id.day_2,
                'time_period': e.section_id.time_slot_id.period_id.start_time.strftime('%H:%M %p') + "-"
                               + e.section_id.time_slot_id.period_id.end_time.strftime('%H:%M %p'),
                'seats_taken': e.section_id.seats_taken,
                'seating_capacity': e.section_id.room_id.capacity,
                'prerequisites': prereq_array
            })

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_student': self.is_student,
                'header_text': 'Update/Drop Courses'
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered,
            'sections': sections_array
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = {
            'is_successful': False
        }
        if request.is_ajax():
            user = request.user
            userprofile = UserProfile.objects.get(user=user)
            student = Student.objects.get(pk=userprofile.student.student_id_id)
            section_id = request.POST.get('section_id')
            section = Section.objects.get(pk=int(section_id))
            enrollment = Enrollment.objects.get(student_id=student, section_id=section)
            enrollment.delete()
            section.seats_taken = section.seats_taken - 1
            section.save()
            data['is_successful'] = True
        else:
            data['is_successful'] = False
        return JsonResponse(data)


class RegisterCourse(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/register_course.html'
    is_student = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_student():
                self.is_student = True
            else:
                return redirect('/student_system/')

        if request.is_ajax():
            department_id = request.GET.get('department_id')
            department_name = request.GET.get('department_name')
            course_id = request.GET.get('course_id')
            days_id = request.GET.get('days_id')
            faculty_id = request.GET.get('faculty_id')
            period_id = request.GET.get('period_id')
            section = None
            # print(department_id)
            # print(department_name)
            # if department_id == '---------' and course_id == '---------' and
            if department_id is not None and department_id != '':
                section = Section.objects.filter(course_id__department_id_id=int(department_id),
                                                 semester_id__status='OPEN_REGISTRATION')
            elif course_id is not None and course_id != '':
                section = Section.objects.filter(course_id=int(course_id), semester_id__status='OPEN_REGISTRATION')
            elif days_id is not None and days_id != '':
                section = Section.objects.filter(time_slot_id__days_id=int(days_id),
                                                 semester_id__status='OPEN_REGISTRATION')
            elif faculty_id is not None and faculty_id != '':
                section = Section.objects.filter(faculty_id=int(faculty_id), semester_id__status='OPEN_REGISTRATION')
            elif period_id is not None and period_id != '':
                section = Section.objects.filter(time_slot_id__period_id=int(period_id),
                                                 semester_id__status='OPEN_REGISTRATION')
            else:
                section = Section.objects.all()

            student_id = user.userprofile.student.student_id_id
            section_array = []
            for s in section:
                # print(s)
                # print("here\n")
                can_register = True
                prerequisites_array = []
                for p in Prerequisite.objects.filter(course_id=s.course_id):
                    prerequisites_array.append({
                        'prerequisite_name': p.course_required_id.name,
                        'prerequisite_id': p.course_required_id.course_id
                    })
                for e in Enrollment.objects.filter(section_id__semester_id__status='OPEN_REGISTRATION'):
                    if e.student_id_id == student_id:
                        if (e.section_id.time_slot_id.period_id.start_time == s.time_slot_id.period_id.start_time
                            and (e.section_id.time_slot_id.days_id.day_1 == s.time_slot_id.days_id.day_1
                                 or e.section_id.time_slot_id.days_id.day_2 == s.time_slot_id.days_id.day_2)) \
                                or (e.section_id.time_slot_id.period_id.end_time == s.time_slot_id.period_id.end_time
                                    and (e.section_id.time_slot_id.days_id.day_1 == s.time_slot_id.days_id.day_1
                                         or e.section_id.time_slot_id.days_id.day_2 == s.time_slot_id.days_id.day_2)):
                            can_register = False
                data = {
                    'section_id': s.section_id,
                    'semester_info': s.semester_id.season + '-' + str(s.semester_id.year) + '--' + s.semester_id.status,
                    'course_id': s.course_id.course_id,
                    'course_department': s.course_id.department_id.name,
                    'course_name': s.course_id.name,
                    'faculty_id': s.faculty_id.faculty_id_id,
                    'faculty_name': s.faculty_id.faculty_id.user.first_name + " " + s.faculty_id.faculty_id.user.last_name,
                    'credits': s.course_id.credits,
                    'seats_taken': s.seats_taken,
                    'seating_capacity': s.room_id.capacity,
                    'time_slot_id': s.time_slot_id.time_slot_id,
                    'prerequisites_array': prerequisites_array,
                    'time_period_id': s.time_slot_id.period_id.period_id,
                    'time_period_range': s.time_slot_id.period_id.start_time.strftime('%H:%M %p')
                                         + " " + s.time_slot_id.period_id.end_time.strftime('%H:%M %p'),
                    'meeting_days_id': s.time_slot_id.days_id.days_id,
                    'meeting_days': s.time_slot_id.days_id.day_1 + " " + s.time_slot_id.days_id.day_2,
                    'building_id': s.room_id.building_id.building_id,
                    'building_name': s.room_id.building_id.name,
                    'room_id': s.room_id.room_id,
                    'room_number': s.room_id.room_number,
                    'can_register': can_register
                }
                section_array.append(data)

            return HttpResponse(json.dumps(section_array), content_type="application/json")

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_student': self.is_student,
                'header_text': 'Register Courses'
            },
            to_static_markup=False,
        )
        departments = Department.objects.all()
        days = MeetingDays.objects.all()
        course = Course.objects.all()
        time_periods = Period.objects.all()
        faculty = []
        for f in Faculty.objects.raw("SELECT u.first_name, u.last_name, f.faculty_id_id "
                                     "FROM registration_system_faculty AS f, auth_user as u, registration_system_userprofile as up "
                                     "WHERE up.user_id = u.id "
                                     "AND up.id = f.faculty_id_id"):
            faculty.append({
                'first_name': f.first_name,
                'last_name': f.last_name,
                'faculty_id': f.faculty_id_id
            })

        context = {
            'rendered': rendered,
            'departments': departments,
            'days': days,
            'faculty': faculty,
            'courses': course,
            'time_periods': time_periods
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = {
            'is_successful': False
        }
        if request.is_ajax():
            user = request.user
            userprofile = UserProfile.objects.get(user=user)
            student = Student.objects.get(pk=userprofile.student.student_id_id)
            section_id = request.POST.get('section_id')
            section = Section.objects.get(pk=int(section_id))
            try:
                student_hold = StudentHold.objects.get(student_id=student)
                data['is_successful'] = False
                data['has_hold'] = True
            except StudentHold.DoesNotExist:
                current_enrollments = Enrollment.objects.filter(student_id=student)
                for e in current_enrollments:
                    if e.section_id.time_slot_id == section.time_slot_id:
                        data['is_successful'] = False
                        data['time_conflict'] = True
                        return JsonResponse(data)
                if section.course_id.has_prerequisites():
                    prerequisites = Prerequisite.objects.filter(course_id=section.course_id)
                    prerequisite_fulfilled = False
                    for e in current_enrollments:
                        for p in prerequisites:
                            if p.course_required_id == e.section_id.course_id:
                                prerequisite_fulfilled = True
                                break
                        else:
                            continue
                        break
                    if not prerequisite_fulfilled:
                        data['is_successful'] = False
                        data['unfulfilled_prerequisite'] = True
                        # if e.section_id.course_id == section.course_id.p
                enrollment = Enrollment.objects.create(student_id=student, section_id=section)
                # meeting = Meetings.objects.create(enrollment_id=enrollment, student_id=student)
                student_history = StudentHistory.objects.create(student_id=student, enrollment_id=enrollment)
                section.seats_taken = section.seats_taken + 1
                section.save()
                data['is_successful'] = True
        else:
            data['is_successful'] = False
        return JsonResponse(data)


class ChangeSemesterStatus(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/change_semester.html'
    is_admin = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_admin():
                self.is_admin = True
            else:
                return redirect('/student_system/')

        semesters = Semester.objects.all()

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_admin': self.is_admin,
                'header_text': 'Create Advising'
            },
            to_static_markup=False,
        )
        context = {
            'rendered': rendered,
            'semesters': semesters
        }

        return render(request, self.template_name, context)

    # TODO: Add more logic to remove students who do not fulfill prerequisites if closing from open_registration
    def post(self, request, *args, **kwargs):
        data = {
            'is_successful': False
        }
        if request.is_ajax():
            semester_id = request.POST.get('semester_id')
            status = request.POST.get('status')
            semester = Semester.objects.get(pk=int(semester_id))
            student_disenrolled = []
            if semester.status == 'OPEN_REGISTRATION':
                if status == 'CLOSE':
                    for e in Enrollment.objects.filter(section_id__semester_id_id=int(semester_id)):
                        try:
                            prerequisites = Prerequisite.objects.filter(course_id=e.section_id.course_id)
                            enrolled_student = Student.objects.get(student_id=e.student_id)
                            for se in Enrollment.objects.filter(student_id=enrolled_student):
                                for p in prerequisites:
                                    if se.section_id.course_id_id == p.course_required_id_id:
                                        if se.grade in ['A', 'A-', 'B', 'B-', 'C']:
                                            continue
                                        else:
                                            student_disenrolled.append({
                                                'student_name': se.student_id.student_id.user.first_name + ' '
                                                + se.student_id.student_id.user.last_name,
                                                'class_dropped': e.section_id.course_id.name,
                                                'section_id_dropped': e.section_id_id
                                            })
                                            se.delete()
                                    else:
                                        student_disenrolled.append({
                                            'student_name': se.student_id.student_id.user.first_name + ' '
                                            + se.student_id.student_id.user.last_name,
                                            'class_dropped': e.section_id.course_id.name,
                                            'section_id_dropped': e.section_id_id
                                        })
                                        se.delete()
                        except Prerequisite.DoesNotExist:
                            continue
            semester.status = status
            semester.save()
            data['is_successful'] = True
            data['students_disenrolled'] = student_disenrolled
        else:
            data['is_successful'] = False
        return JsonResponse(data)


class CreateAdvising(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/create_advising.html'
    is_admin = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_admin():
                self.is_admin = True
            else:
                return redirect('/student_system/')

        if request.is_ajax():
            first_name = request.GET.get('first_name')
            last_name = request.GET.get('last_name')
            # user = User.objects.filter(Q(username=username) | Q(email=email) | Q(first_name=first_name) |
            #                            Q(last_name=last_name))
            user = User.objects.get(first_name=first_name, last_name=last_name)

            is_advised = True
            try:
                student = Student.objects.get(pk=int(user.userprofile.student.student_id_id))
                advising = Advising.objects.get(student_id=student)
            except Advising.DoesNotExist:
                is_advised = False

            faculty = []
            for f in Faculty.objects.raw("SELECT u.first_name, u.last_name, f.faculty_id_id "
                                         "FROM registration_system_faculty AS f, auth_user as u, registration_system_userprofile as up "
                                         "WHERE up.user_id = u.id "
                                         "AND up.id = f.faculty_id_id"):
                faculty.append({
                    'first_name': f.first_name,
                    'last_name': f.last_name,
                    'full_name': f.first_name + " " + f.last_name,
                    'faculty_id': f.faculty_id_id
                })

            data = {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'isAdvised': is_advised,
                'faculty_array': faculty
            }

            return HttpResponse(json.dumps(data), content_type="application/json")

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_admin': self.is_admin,
                'header_text': 'Create Advising'
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = {
            'is_successful': False
        }
        if request.is_ajax():
            user_id = request.POST.get('userID')
            faculty_id = request.POST.get('faculty')
            faculty = Faculty.objects.get(pk=int(faculty_id))
            # = request.POST.get('hold')
            is_update = request.POST.get('isUpdate')
            student = Student.objects.get(student_id__user_id=user_id)
            if is_update is not None:
                # TODO: Update advising
                advising = Advising.objects.get(student_id=student)
                advising.faculty_id = faculty
                advising.save()
                data['is_successful'] = True
                return JsonResponse(data)
            advising = Advising.objects.create(faculty_id=faculty, student_id=student)
            data['is_successful'] = True
        else:
            data['is_successful'] = False
        return JsonResponse(data)


class ViewHold(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/view_hold.html'
    is_student = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_student():
                self.is_student = True
            else:
                return redirect('/student_system/')
        hold = None
        try:
            student = Student.objects.get(pk=int(user.userprofile.student.student_id_id))
            hold = StudentHold.objects.get(student_id=student)
            # hold.hold_id.name
            # print(hold)
        except StudentHold.DoesNotExist:
            hold = None

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_student': self.is_student,
                'header_text': 'View Hold'
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered,
            'holds': hold
        }

        return render(request, self.template_name, context)


class ViewAdvisees(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/view_advisees.html'
    is_faculty = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_faculty():
                self.is_faculty = True
            else:
                return redirect('/student_system/')

        try:
            faculty = Faculty.objects.get(pk=int(user.userprofile.faculty.faculty_id_id))
            advising = Advising.objects.filter(faculty_id=faculty)
            faculty_name = faculty.faculty_id.user.first_name + ' ' + faculty.faculty_id.user.last_name
            students = []
            for a in advising:
                students.append({
                    'student_name': a.student_id.student_id.user.first_name+" "+a.student_id.student_id.user.last_name,
                    'student_email': a.student_id.student_id.user.email,
                    'student_username': a.student_id.student_id.user.username
                })
        except Advising.DoesNotExist:
            advising = None
            faculty_name = None
            students = None

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_faculty': self.is_faculty,
                'header_text': 'View Advisee'
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered,
            'advising': advising,
            'faculty_name': faculty_name,
            'students': students
        }

        return render(request, self.template_name, context)


class ViewAdvising(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/view_adviser.html'
    is_student = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_student():
                self.is_student = True
            else:
                return redirect('/student_system/')
        advising = None
        faculty_name = None
        try:
            student = Student.objects.get(pk=int(user.userprofile.student.student_id_id))
            advising = Advising.objects.get(student_id=student)
            faculty_name = advising.faculty_id.faculty_id.user.first_name + ' ' + advising.faculty_id.faculty_id.user.last_name
        except Advising.DoesNotExist:
            advising = None
            faculty_name = None

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_student': self.is_student,
                'header_text': 'View Adviser'
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered,
            'advising': advising,
            'faculty_name': faculty_name

        }

        return render(request, self.template_name, context)


class CreateHold(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/create_hold.html'
    is_admin = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_admin():
                self.is_admin = True
            else:
                return redirect('/student_system/')

        if request.is_ajax():
            first_name = request.GET.get('first_name')
            last_name = request.GET.get('last_name')
            # user = User.objects.filter(Q(username=username) | Q(email=email) | Q(first_name=first_name) |
            #                            Q(last_name=last_name))
            user = User.objects.get(first_name=first_name, last_name=last_name)

            is_held = False
            try:
                student = Student.objects.get(pk=int(user.userprofile.student.student_id_id))
                hold = StudentHold.objects.get(student_id=student)
                is_held = True
            except StudentHold.DoesNotExist:
                is_held = False

            data = {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'isHeld': is_held
            }

            return HttpResponse(json.dumps(data), content_type="application/json")

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_admin': self.is_admin,
                'header_text': 'Create Hold'
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = {
            'is_successful': False
        }
        if request.is_ajax():
            user_id = request.POST.get('userID')
            hold = request.POST.get('hold')
            is_remove = request.POST.get('isRemove')
            user = User.objects.get(pk=int(user_id))
            if is_remove is not None:
                student = Student.objects.get(pk=int(user.userprofile.student.student_id_id))
                student_hold = StudentHold.objects.get(student_id=student)
                student_hold.delete()
                data['is_successful'] = True
                return JsonResponse(data)
            hold = Hold.objects.create(name=hold)

            student_id = user.userprofile.student.student_id_id
            student = Student.objects.get(pk=int(student_id))
            student_hold = StudentHold.objects.create(student_id=student, hold_id=hold)
            data['is_successful'] = True
        else:
            data['is_successful'] = False
        return JsonResponse(data)


class UpdateSection(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/search_section.html'
    is_admin = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_admin():
                self.is_admin = True
            else:
                return redirect('/student_system/')

        if request.is_ajax():
            department_id = request.GET.get('department_id')
            department_name = request.GET.get('department_name')
            course_id = request.GET.get('course_id')
            days_id = request.GET.get('days_id')
            faculty_id = request.GET.get('faculty_id')
            section = None
            # print(department_id)

            if (course_id is not None and int(course_id) != 0) and (faculty_id is not None and int(faculty_id) != 0) and (days_id is not None and int(days_id) !=0):
                section = Section.objects.filter(faculty_id=int(faculty_id), time_slot_id__days_id=int(days_id),
                                                 course_id=int(course_id))
            if (faculty_id is not None and int(faculty_id) != 0) and (days_id is not None and int(days_id) != 0):
                section = Section.objects.filter(faculty_id=int(faculty_id), time_slot_id__days_id=int(days_id))
            if (department_id is not None and int(department_id) != 0) and (course_id is not None and int(course_id) != 0):
                section = Section.objects.filter(course_id__department_id_id=int(department_id),
                                                 course_id=int(course_id))
            elif (department_id is not None and int(department_id) != 0) and (faculty_id is not None and int(faculty_id) != 0):
                section = Section.objects.filter(course_id__department_id_id=int(department_id),
                                                 faculty_id=int(faculty_id))
            elif (department_id is not None and int(department_id) != 0) and (days_id is not None and int(days_id) != 0):
                section = Section.objects.filter(course_id__department_id_id=int(department_id),
                                                 time_slot_id__days_id=int(days_id))
            elif (course_id is not None and int(course_id) != 0) and (faculty_id is not None and int(faculty_id) != 0):
                section = Section.objects.filter(course_id=int(course_id),
                                                 faculty_id=int(faculty_id))
            elif (course_id is not None and int(course_id) != 0) and (days_id is not None and int(days_id) != 0):
                section = Section.objects.filter(course_id=int(course_id),
                                                 time_slot_id__days_id=int(days_id))
            elif department_id is not None and int(department_id) != 0:
                section = Section.objects.filter(course_id__department_id_id=int(department_id))
            elif course_id is not None and int(course_id) != 0:
                section = Section.objects.filter(course_id=int(course_id))
            elif days_id is not None and int(days_id) != 0:
                section = Section.objects.filter(time_slot_id__days_id=int(days_id))
            elif faculty_id is not None and int(faculty_id) != 0:
                section = Section.objects.filter(faculty_id=int(faculty_id))

            faculty = []
            for f in Faculty.objects.raw("SELECT u.first_name, u.last_name, f.faculty_id_id "
                                         "FROM registration_system_faculty AS f, auth_user as u, registration_system_userprofile as up "
                                         "WHERE up.user_id = u.id "
                                         "AND up.id = f.faculty_id_id"):
                faculty.append({
                    'first_name': f.first_name,
                    'last_name': f.last_name,
                    'full_name': f.first_name + " " + f.last_name,
                    'faculty_id': f.faculty_id_id
                })
            departments = []
            for d in Department.objects.all():
                departments.append({
                    'department_id': d.department_id,
                    'department_name': d.name
                })
            time_periods = []
            for t in Period.objects.all():
                time_periods.append({
                    'time_period_id': t.period_id,
                    'time_range': t.start_time.strftime('%H:%M %p') + ' ' + t.end_time.strftime('%H:%M %p')
                })
            meeting_days = []
            for m in MeetingDays.objects.all():
                if m.day_3:
                    meeting_days.append({
                        'days_id': m.days_id,
                        'day_1': m.day_1,
                        'day_2': m.day_2,
                        'day_3': m.day_3,
                        'day_range': m.day_1 + " " + m.day_2 + " " + m.day_3
                    })
                elif m.day_2 and m.day_3 is None:
                    meeting_days.append({
                        'days_id': m.days_id,
                        'day_1': m.day_1,
                        'day_2': m.day_2,
                        'day_range': m.day_1 + " " + m.day_2
                    })
                elif m.day_1 and m.day_2 is None:
                    meeting_days.append({
                        'days_id': m.days_id,
                        'day_1': m.day_1,
                        'day_range': m.day_1
                    })
            buildings = []
            for b in Building.objects.all():
                buildings.append({
                    'building_id': b.building_id,
                    'building_name': b.name
                })
            rooms = []
            for arrgh in Room.objects.all():
                rooms.append({
                    'rooms_id': arrgh.room_id,
                    'room_number': arrgh.room_number
                })

            section_array = []
            for s in section:
                # print(s)
                # print("here\n")
                data = {
                    'faculty_array': faculty,
                    'departments_array': departments,
                    'time_periods_array': time_periods,
                    'meeting_days_array': meeting_days,
                    'buildings_array': buildings,
                    'semester_id': s.semester_id_id,
                    'semester_year': s.semester_id.year,
                    'semester_season': s.semester_id.season,
                    'semester_status': s.semester_id.status,
                    'rooms_array': rooms,
                    'section_id': s.section_id,
                    'course_id': s.course_id.course_id,
                    'course_department': s.course_id.department_id.name,
                    'course_name': s.course_id.name,
                    'faculty_id': s.faculty_id.faculty_id_id,
                    'faculty_name': s.faculty_id.faculty_id.user.first_name + " " + s.faculty_id.faculty_id.user.last_name,
                    'credits': s.course_id.credits,
                    'seats_taken': s.seats_taken,
                    'seating_capacity': s.room_id.capacity,
                    'time_slot_id': s.time_slot_id.time_slot_id,
                    'time_period_id': s.time_slot_id.period_id.period_id,
                    'time_period_range': s.time_slot_id.period_id.start_time.strftime('%H:%M %p')
                                         + " " + s.time_slot_id.period_id.end_time.strftime('%H:%M %p'),
                    'meeting_days_id': s.time_slot_id.days_id.days_id,
                    'meeting_days': s.time_slot_id.days_id.day_1 + s.time_slot_id.days_id.day_2,
                    'building_id': s.room_id.building_id.building_id,
                    'building_name': s.room_id.building_id.name,
                    'room_id': s.room_id.room_id,
                    'room_number': s.room_id.room_number
                }
                section_array.append(data)

            return HttpResponse(json.dumps(section_array), content_type="application/json")

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_admin': self.is_admin,
                'header_text': 'Update Section'
            },
            to_static_markup=False,
        )
        departments = Department.objects.all()
        days = MeetingDays.objects.all()
        course = Course.objects.all()
        faculty = []
        for f in Faculty.objects.raw("SELECT u.first_name, u.last_name, f.faculty_id_id "
                                     "FROM registration_system_faculty AS f, auth_user as u, registration_system_userprofile as up "
                                     "WHERE up.user_id = u.id "
                                     "AND up.id = f.faculty_id_id"):
            faculty.append({
                'first_name': f.first_name,
                'last_name': f.last_name,
                'faculty_id': f.faculty_id_id
            })

        context = {
            'rendered': rendered,
            'departments': departments,
            'days': days,
            'faculty': faculty,
            'courses': course
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = {
            'is_successful': False
        }
        if request.is_ajax():
            faculty_id = request.POST.get('faculty')
            faculty = Faculty.objects.get(pk=int(faculty_id))
            time_period = request.POST.get('time_period')
            days = request.POST.get('days')
            # print(time_period)
            # print(days)
            try:
                time_slot = TimeSlot.objects.get(days_id=int(days), period_id=int(time_period))
            except TimeSlot.DoesNotExist:
                time_slot = TimeSlot.objects.create(days_id_id=int(days), period_id=Period.objects.get(pk=int(time_period)))
            building_id = request.POST.get('building')
            building = Building.objects.get(pk=int(building_id))
            room_id = request.POST.get('room')
            room = Room.objects.get(pk=int(room_id))
            section_id = request.POST.get('section_id')
            section = Section.objects.get(pk=int(section_id))
            section.faculty_id = faculty
            section.time_slot_id = time_slot
            section.building_id = building
            section.room_id = room
            section.save()
            data['is_successful'] = True
        else:
            data['is_successful'] = False
        return JsonResponse(data)


class CreateSection(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/create_section.html'
    is_admin = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)
        if userprofile:
            if userprofile.has_admin():
                self.is_admin = True
            else:
                return redirect('/student_system/')

        departments = Department.objects.all()
        buildings = Building.objects.all()
        semester = Semester.objects.all()
        days = MeetingDays.objects.all()
        time_period = Period.objects.all()
        faculty = []
        for f in Faculty.objects.raw("SELECT u.first_name, u.last_name, f.faculty_id_id "
                                     "FROM registration_system_faculty AS f, auth_user as u, registration_system_userprofile as up "
                                     "WHERE up.user_id = u.id "
                                     "AND up.id = f.faculty_id_id"):
            faculty.append({
                'first_name': f.first_name,
                'last_name': f.last_name,
                'faculty_id': f.faculty_id_id
            })

        if request.is_ajax():
            building_number = request.GET.get('building_id')
            if building_number is not None:
                rooms = Room.objects.filter(building_id__building_id=int(building_number))
                rooms_array = []
                for r in rooms:
                    data = {
                        'room_id': r.room_id,
                        'room_number': r.room_number,
                        'room_type': r.type,
                        'room_capacity': r.capacity
                    }
                    rooms_array.append(data)
                return HttpResponse(json.dumps(rooms_array), content_type="application/json")
            else:
                department_id = request.GET.get('department_id')
                department_name = request.GET.get('department_name')

                # user = User.objects.filter(Q(username=username) | Q(email=email) | Q(first_name=first_name) |
                #                            Q(last_name=last_name))
                courses = Course.objects.filter(department_id=int(department_id))
                course_array = []
                for c in courses:
                    # print(c)
                    data = {
                        'course_id': c.course_id,
                        'department_name': department_name,
                        'department_id': department_id,
                        'course_name': c.name,
                        'course_description': c.description,
                        'course_credits': c.credits
                    }
                    course_array.append(data)
                faculty_array = []
                for f in Faculty.objects.filter(department_id=int(department_id)):
                    data = {
                        'faculty_name': f.faculty_id.user.first_name + ' ' + f.faculty_id.user.last_name,
                        'faculty_id': f.faculty_id_id

                    }
                    faculty_array.append(data)
                data_obj = {
                    'faculty_array': faculty_array,
                    'course_array': course_array
                }
                return HttpResponse(json.dumps(data_obj), content_type="application/json")

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_admin': self.is_admin,
                'header_text': 'Create Section'
            },
            to_static_markup=False,
        )
        return render(request, self.template_name, {'rendered': rendered, 'departments': departments,
                                                    'buildings': buildings, 'semesters': semester, 'days': days,
                                                    'time_periods': time_period, 'faculty': faculty})

    def post(self, request, *args, **kwargs):
        data = {
            'is_successful': False
        }
        if request.is_ajax():
            department = request.POST.get('department')
            course_id = request.POST.get('course')
            course = Course.objects.get(pk=int(course_id))
            faculty_id = request.POST.get('faculty')
            faculty = Faculty.objects.get(pk=int(faculty_id))
            building_id = request.POST.get('building')
            building = Building.objects.get(pk=int(building_id))
            room_id = request.POST.get('room')
            room = Room.objects.get(pk=int(room_id))
            semester_id = request.POST.get('semester')
            semester = Semester.objects.get(pk=int(semester_id))
            days_id = request.POST.get('days')
            days = MeetingDays.objects.get(pk=int(days_id))
            time_period_id = request.POST.get('time_period')
            time_period = Period.objects.get(pk=int(time_period_id))
            time_slot = None
            try:
                time_slot = TimeSlot.objects.get(days_id=days, period_id=time_period)
            except TimeSlot.DoesNotExist:
                time_slot = TimeSlot.objects.create(days_id=days, period_id=time_period)
            section = Section.objects.create(course_id=course, time_slot_id=time_slot,
                                             faculty_id=faculty, semester_id=semester, room_id=room)
            data['is_successful'] = True
        else:
            data['is_successful'] = False
        return JsonResponse(data)


class UpdateCourse(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/search_course.html'
    is_admin = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_admin():
                self.is_admin = True
            else:
                return redirect('/student_system/')

        if request.is_ajax():
            department_id = request.GET.get('department_id')
            department_name = request.GET.get('department_name')
            # user = User.objects.filter(Q(username=username) | Q(email=email) | Q(first_name=first_name) |
            #                            Q(last_name=last_name))
            courses = Course.objects.filter(department_id=int(department_id))
            course_array = []
            for c in courses:
                # print(c)
                data = {
                    'course_id': c.course_id,
                    'department_name': department_name,
                    'department_id': department_id,
                    'course_name': c.name,
                    'course_description': c.description,
                    'course_credits': c.credits
                }
                course_array.append(data)
            return HttpResponse(json.dumps(course_array), content_type="application/json")

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_admin': self.is_admin,
                'header_text': 'Search Course'
            },
            to_static_markup=False,
        )
        departments = Department.objects.all()
        context = {
            'rendered': rendered,
            'departments': departments
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = {
            'is_successful': False
        }
        if request.is_ajax():
            course_id = request.POST.get('courseID')
            course_name = request.POST.get('courseName')
            course_description = request.POST.get('course_description')
            course_credits = request.POST.get('course_credits')
            course = Course.objects.get(pk=int(course_id))
            course.name = course_name
            course.description = course_description
            course.credits = course_credits
            course.save()
            data['is_successful'] = True
        else:
            data['is_successful'] = False
        return JsonResponse(data)


class UpdateUser(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/search_user.html'
    is_admin = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_admin():
                self.is_admin = True
            else:
                return redirect('/student_system/')

        if request.is_ajax():
            first_name = request.GET.get('first_name')
            last_name = request.GET.get('last_name')
            email = request.GET.get('email')
            username = request.GET.get('username')
            user_type = request.GET.get('user_type')
            # user = User.objects.filter(Q(username=username) | Q(email=email) | Q(first_name=first_name) |
            #                            Q(last_name=last_name))
            if first_name and last_name:
                user = User.objects.filter(first_name=first_name, last_name=last_name)
            if username:
                user = User.objects.filter(username=username)
            elif email:
                user = User.objects.filter(email=email)
            elif user_type and user_type != '0':
                if user_type == 'faculty':
                    user = User.objects.filter(userprofile__user_type='F')
                elif user_type == 'admin':
                    user = User.objects.filter(userprofile__user_type='A')
                elif user_type == 'student':
                    user = User.objects.filter(userprofile__user_type='S')
                elif user_type == 'researcher':
                    user = User.objects.filter(userprofile__user_type='R')
            elif first_name:
                user = User.objects.filter(first_name=first_name)
            elif last_name:
                user = User.objects.filter(last_name=last_name)
            user_array = []
            for u in user:
                # print(u)
                user_profile = UserProfile.objects.get(user_id=u.id)
                data = {
                    'user_id': u.id,
                    'username': u.username,
                    'email': u.email,
                    'first_name': u.first_name,
                    'last_name': u.last_name,
                    'user_type': user_profile.user_type
                }
                if user_profile.has_faculty():
                    data['department_name'] = user_profile.faculty.department_id.name
                user_array.append(data)
            return HttpResponse(json.dumps(user_array), content_type="application/json")

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_admin': self.is_admin,
                'header_text': 'Search User'
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = {
            'is_successful': False
        }
        if request.is_ajax():
            user_id = request.POST.get('userID')
            user = User.objects.get(pk=int(user_id))
            user.delete()
            data['is_successful'] = True
        else:
            data['is_successful'] = False
        return JsonResponse(data)


# TODO: Create Post Method and create get method for Department RESTful query
class CreateUser(LoginRequiredMixin, generic.View):
    user_form_class = CreateUserParentForm
    user_profile_form_class = CreateUserProfileForm
    student_form_class = CreateStudentForm
    faculty_form_class = CreateFacultyForm
    template_name = 'registration_system/create_user.html'
    is_admin = False

    def get(self, request, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_admin():
                self.is_admin = True
            else:
                return redirect('/student_system/')

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_admin': self.is_admin,
                'header_text': 'Create User'
            },
            to_static_markup=False,
        )

        context = {
            'rendered': rendered
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = {
            'is_successful': False
        }
        if request.POST:

            user_form = self.user_form_class(request.POST, instance=User())
            user_profile_form = self.user_profile_form_class(request.POST, instance=UserProfile())
            # print(user_form.errors)
            # print(user_profile_form.errors)
            if user_form.is_valid() and user_profile_form.is_valid():
                username = user_form.cleaned_data['username']
                password = user_form.cleaned_data['password']
                first_name = user_form.cleaned_data['first_name']
                last_name = user_form.cleaned_data['last_name']
                email = user_form.cleaned_data['email']
                user_type = user_profile_form.cleaned_data['user_type']
                user = User.objects.create_user(username=username, password=password, first_name=first_name,
                                                last_name=last_name, email=email)
                user_profile = user.userprofile
                if user_type == 'A':
                    user_profile.user_type = 'A'
                    user_profile.save()
                    admin = Admin.objects.create(admin_id=user_profile)
                    data['is_successful'] = True
                    # print(admin)
                elif user_type == 'R':
                    user_profile.user_type = 'R'
                    user_profile.save()
                    researcher = Researcher.objects.create(researcher_id=user_profile)
                    data['is_successful'] = True
                elif user_type == 'S':
                    student_form = self.student_form_class(request.POST, instance=Student())
                    if student_form.is_valid():
                        date_of_birth = student_form.cleaned_data['date_of_birth']
                        student_type = student_form.cleaned_data['student_type']
                        credits_variable = None
                        if request.POST.get("credits") != 0:
                            credits_variable = request.POST.get("credits")
                            user_profile.user_type = 'S'
                            user_profile.save()
                            student = Student.objects.create(student_id=user_profile, date_of_birth=date_of_birth,
                                                             student_type=student_type.strip())
                            if student.student_type == 'F':
                                student.fulltimestudent.credits = int(credits_variable)
                                student.fulltimestudent.save()
                            else:
                                student.parttimestudent.credits = int(credits_variable)
                                student.parttimestudent.save()
                        else:
                            user_profile.user_type = 'S'
                            user_profile.save()
                            student = Student.objects.create(student_id=user_profile, date_of_birth=date_of_birth,
                                                             student_type=student_type.strip())
                        data['is_successful'] = True
                elif user_type == 'F':
                    faculty_form = self.faculty_form_class(request.POST, instance=Faculty())
                    if faculty_form.is_valid():
                        department_id = faculty_form.cleaned_data['department_id']
                        faculty_type = faculty_form.cleaned_data['faculty_type']
                        user_profile.user_type = 'F'
                        user_profile.save()
                        faculty = Faculty.objects.create(faculty_id=user_profile, department_id=department_id,
                                                         faculty_type=faculty_type.strip())
                        data['is_successful'] = True
                        # print(faculty)
                # data['errors'] = self.user_form_class.errors if self.user_form_class.errors else None
                # data['errors'] = self.user_profile_form_class.errors if self.user_profile_form_class.errors else None
                # data['errors'] = self.faculty_form_class.errors if self.faculty_form_class.errors else None
                # data['errors'] = self.student_form_class.errors if self.student_form_class.errors else None
                return JsonResponse(data)


class CreatePrerequisite(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/create_prerequisite.html'
    is_admin = False

    def get(self, request, course_id, *args, **kwargs):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)

        if userprofile:
            if userprofile.has_admin():
                self.is_admin = True
            else:
                return redirect('/student_system/')

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_admin': self.is_admin,
                'header_text': 'Create Prerequisites'
            },
            to_static_markup=False,
        )

        courses = Course.objects.all()
        context = {
            'courses': courses,
            'rendered': rendered,
            'value': course_id
        }
        return render(request, self.template_name, context)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            message = "Ajax"
            course_id = request.POST.get('courseID')
            prerequisites = json.loads(request.POST.get('prerequisites'))
            course = Course.objects.get(pk=int(course_id))
            for p in prerequisites:
                prerequisite_course = Course.objects.get(pk=int(p))
                Prerequisite.objects.create(course_id=course, course_required_id=prerequisite_course)
        else:
            message = "No Ajax"
        return HttpResponse(message)


# TODO: Finish Create Course, create permission_error  view and template
# TODO: Finish create course success view and template, figure out if the way I'm using redirect is optimal.
class CreateCourse(LoginRequiredMixin, generic.View):
    form_class = CreateCourseForm
    template_name = 'registration_system/create_course.html'
    is_admin = False

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        user = request.user
        userprofile = UserProfile.objects.get(user=user)
        if userprofile:
            if userprofile.has_admin():
                self.is_admin = True
            else:
                return redirect('/student_system/')

        departments = Department.objects.all()

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'nav-holder.jsx'),
            {
                'is_admin': self.is_admin,
                'header_text': 'Create Course'
            },
            to_static_markup=False,
        )
        return render(request, self.template_name, {'rendered': rendered, 'form': form, 'departments': departments})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        # print(form.is_valid())
        # print(form.errors)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            credits_value = form.cleaned_data['credits']
            department_id = form.cleaned_data['department_id']
            course = Course.objects.create(name=name, description=description, credits=credits_value,
                                           department_id=department_id)
            return redirect('create_prerequisites', course_id=course.course_id)
        return redirect('/student_system/create_course/')


class UserDisplay(LoginRequiredMixin, generic.View):
    template_name = 'registration_system/user_display.html'
    is_part_time_student = False
    is_full_time_student = False
    is_part_time_faculty = False
    is_full_time_faculty = False
    is_faculty = False
    is_admin = False
    is_researcher = False
    bg_img = 'registration_system/images/college_bg_img.jpg'

    def get(self, request):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)
        if userprofile:
            if userprofile.has_student():
                student = Student.objects.get(student_id=userprofile)
                self.bg_img = 'registration_system/images/student_display_bg.jpg'
                if student.has_full_time_student():
                    self.is_full_time_student = True
                elif student.has_part_time_student():
                    self.is_part_time_student = True
            elif userprofile.has_admin():
                self.is_admin = True
            elif userprofile.has_researcher():
                self.bg_img = 'registration_system/images/researcher_display_bg.jpg'
                self.is_researcher = True
            elif userprofile.has_faculty():
                self.bg_img = 'registration_system/images/faculty_display_bg.jpg'
                faculty = Faculty.objects.get(faculty_id=userprofile)
                # print(faculty)
                self.is_faculty = True
        is_student = self.is_full_time_student or self.is_part_time_student

        rendered = render_component(
            os.path.join(os.getcwd(), 'registration_system', 'static',
                         'registration_system', 'js', 'user-display.jsx'),
            {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_admin': self.is_admin,
                'is_full_time_student': self.is_full_time_student,
                'is_part_time_student': self.is_part_time_student,
                'is_faculty': self.is_faculty,
                'is_researcher': self.is_researcher,
                'is_student': is_student,
                'bg_img': self.bg_img
            },
            to_static_markup=False,
        )
        return render(request, self.template_name, {'rendered': rendered, 'user': user, 'bg_img': self.bg_img})


# TODO: Finish CSV Report
def get_csv_report(request):
    grading_key = {
        'A': 4.0,
        'A-': 3.5,
        'B': 3.0,
        'B-': 2.5,
        'C': 2.0,
        'C-': 1.5,
        'D': 1.0,
        'D-': 0.5,
        'F': 0
    }
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    writer = csv.writer(response)
    writer.writerow(['Student Name', 'Grade'])

    for s in Student.objects.all():
        enrollments = Enrollment.objects.filter(student_id=s)
        # enrollments_array = []
        grades = 0.0
        counter = 0
        for e in enrollments:
            if e.grade != 'I' and e.grade != 'W' and e.grade != 'NA':
                grades += grading_key[e.grade]

            counter = counter + 1

        if grades == 0.0 and counter == 0:
            cumulative_gpa = 0.0
        else:
            cumulative_gpa = float(grades / counter)
        writer.writerow(['Student_' + str(s.student_id_id), cumulative_gpa])

    return response


def get_attendance_csv_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    writer = csv.writer(response)
    writer.writerow(['Class', 'Tally'])

    course_name = {}
    for c in Course.objects.all():
        course_name[c.name] = {
            'tally': 0
        }

    for s in Section.objects.all():
        course_name[s.course_id.name]['tally'] = course_name[s.course_id.name]['tally'] + s.seats_taken
    # print(meeting_dates)

    for key, value in course_name.items():
        writer.writerow([key, value['tally']])

    return response


def get_departments(request):
    departments = Department.objects.all()
    department_array = []
    for d in departments:
        data = {
            'department_id': d.department_id,
            'department_name': d.name
        }
        department_array.append(data)
    return HttpResponse(json.dumps(department_array), content_type="application/json")


def create_time_slot(request):
    data = {
        'is_successful': False
    }
    if request.is_ajax():
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        Period.objects.create(start_time=start_time, end_time=end_time)
        data['is_successful'] = True
    else:
        data['is_successful'] = False
    return JsonResponse(data)


def get_grading_sections(request):
    user = request.user
    faculty_id = user.userprofile.faculty
    if request.is_ajax():
        semester_id = request.GET.get('semester_id')
        sections_array = []
        for e in Enrollment.objects.filter(section_id__faculty_id=faculty_id,
                                           section_id__semester_id__semester_id=int(semester_id)):
            prerequisites = Prerequisite.objects.filter(course_id=e.section_id.course_id)
            prereq_array = []
            for p in prerequisites:
                prereq_array.append({
                    'name': p.course_required_id.name
                })
            faculty_name = e.section_id.faculty_id.faculty_id.user.first_name + " " + e.section_id.faculty_id.faculty_id.user.last_name
            sections_array.append({
                'section_id': e.section_id_id,
                'course_name': e.section_id.course_id.name,
                'professor': faculty_name,
                'credits': e.section_id.course_id.credits,
                'room_number': e.section_id.room_id.room_number,
                'building': e.section_id.room_id.building_id.name,
                'meeting_days': e.section_id.time_slot_id.days_id.day_1 + " " + e.section_id.time_slot_id.days_id.day_2,
                'time_period': e.section_id.time_slot_id.period_id.start_time.strftime('%H:%M %p') + "-"
                               + e.section_id.time_slot_id.period_id.end_time.strftime('%H:%M %p'),
                'seats_taken': e.section_id.seats_taken,
                'seating_capacity': e.section_id.room_id.capacity,
                'prerequisites': prereq_array,
                'semester_season': e.section_id.semester_id.season,
                'semester_year': e.section_id.semester_id.year,
                'semester_status': e.section_id.semester_id.status
            })
        data = {
            'sections_array': sections_array,
            'faculty_name': user.first_name + " " + user.last_name,
            'is_successful': True
        }
    else:
        data = {
            'is_successful': False
        }
    return JsonResponse(data)


def get_master_schedule_search_data(request, attribute_flag, search_value):
    section = None
    schedule_data = []
    if attribute_flag == 'department':
        section = Section.objects.filter(course_id__department_id_id=int(search_value))
    elif attribute_flag == 'faculty':
        section = Section.objects.filter(faculty_id__faculty_id_id=int(search_value))
    elif attribute_flag == 'days':
        section = Section.objects.filter(time_slot_id__days_id_id=int(search_value))
    elif attribute_flag == 'time_period':
        section = Section.objects.filter(time_slot_id__period_id_id=int(search_value))
    elif attribute_flag == 'building':
        section = Section.objects.filter(course_id__department_id__building_id_id=int(search_value))
    elif attribute_flag == 'rooms':
        section = Section.objects.filter(room_id_id=int(search_value))
    elif attribute_flag == 'course_name':
        section = Section.objects.filter(course_id__name__contains=search_value)
    elif attribute_flag == 'semester':
        section = Section.objects.filter(semester_id=int(search_value))

    for s in section:
        faculty = Faculty.objects.get(pk=int(s.faculty_id_id))
        faculty_name = faculty.faculty_id.user.first_name + ' ' + faculty.faculty_id.user.last_name
        prerequisites = Prerequisite.objects.filter(course_id=s.course_id)
        prereq_array = []
        for p in prerequisites:
            prereq_array.append({
                'name': p.course_required_id.name
            })
        data = {
            'faculty': faculty_name,
            'course_name': s.course_id.name,
            'course_description': s.course_id.description,
            'department': s.course_id.department_id.name,
            'semester_year': s.semester_id.year,
            'semester_season': s.semester_id.season,
            'semester_status': s.semester_id.status,
            'section_id': s.section_id,
            'credits' : s.course_id.credits,
            'seats_taken': s.seats_taken,
            'capacity': s.room_id.capacity,
            'meeting_days': s.time_slot_id.days_id.day_1 + ' ' + s.time_slot_id.days_id.day_2,
            'time_period': s.time_slot_id.period_id.start_time.strftime('%H:%M %p') + '-'
                           + s.time_slot_id.period_id.end_time.strftime('%H:%M %p'),
            'room': s.room_id.room_number,
            'building': s.room_id.building_id.name,
            'prerequisites': prereq_array
        }
        schedule_data.append(data)

    return HttpResponse(json.dumps(schedule_data), content_type="application/json")


def get_master_schedule_input_data(request):
    departments = Department.objects.all()
    general_data = {}
    department_array = []
    for d in departments:
        data = {
            'department_id': d.department_id,
            'department_name': d.name
        }
        department_array.append(data)
    faculty = []
    for f in Faculty.objects.raw("SELECT u.first_name, u.last_name, f.faculty_id_id "
                                 "FROM registration_system_faculty AS f, auth_user as u, registration_system_userprofile as up "
                                 "WHERE up.user_id = u.id "
                                 "AND up.id = f.faculty_id_id"):
        faculty.append({
            'first_name': f.first_name,
            'last_name': f.last_name,
            'full_name': f.first_name + " " + f.last_name,
            'faculty_id': f.faculty_id_id
        })
    time_periods = []
    for t in Period.objects.all():
        time_periods.append({
            'time_period_id': t.period_id,
            'time_range': t.start_time.strftime('%H:%M %p') + ' ' + t.end_time.strftime('%H:%M %p')
        })
    meeting_days = []
    for m in MeetingDays.objects.all():
        if m.day_3:
            meeting_days.append({
                'days_id': m.days_id,
                'day_1': m.day_1,
                'day_2': m.day_2,
                'day_3': m.day_3,
                'day_range': m.day_1 + " " + m.day_2 + " " + m.day_3
            })
        elif m.day_2 and m.day_3 is None:
            meeting_days.append({
                'days_id': m.days_id,
                'day_1': m.day_1,
                'day_2': m.day_2,
                'day_range': m.day_1 + " " + m.day_2
            })
        elif m.day_1 and m.day_2 is None:
            meeting_days.append({
                'days_id': m.days_id,
                'day_1': m.day_1,
                'day_range': m.day_1
            })
    buildings = []
    for b in Building.objects.all():
        buildings.append({
            'building_id': b.building_id,
            'building_name': b.name
        })
    rooms = []
    for arrgh in Room.objects.all():
        rooms.append({
            'rooms_id': arrgh.room_id,
            'room_number': arrgh.room_number
        })
    semester = []
    for s in Semester.objects.all():
        semester.append({
            'semester_id': s.semester_id,
            'semester_year': s.year,
            'semester_season': s.season,
            'semester_status': s.status
        })
    # print(semester)
    general_data['semesters'] = semester
    general_data['time_periods'] = time_periods
    general_data['meeting_days'] = meeting_days
    general_data['buildings'] = buildings
    general_data['rooms'] = rooms
    general_data['faculty'] = faculty
    general_data['departments'] = department_array

    return HttpResponse(json.dumps(general_data), content_type="application/json")


class MasterScheduleView(generic.TemplateView):
    template_name = 'registration_system/master_schedule.html'


@csrf_exempt
def get_master_schedule_search_data_v2(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    department_id = body['department_id']
    faculty_id = body['faculty_id']
    days_id = body['days_id']
    time_period_id = body['period_id']
    building_id = body['building_id']
    room_id = body['room_id']
    course_name = body['course_name']
    semester_id = body['semester_id']
    section = None
    schedule_data = []
    # if department_id:
    #     if faculty_id:
    #         pass
    #     elif days_id:
    #         pass
    #     elif time_period_id:
    #         pass
    #     elif building_id:
    #         pass
    #     elif room_id:
    #         pass
    #     elif semester_id:
    #         pass
    #     else:
    #         pass
    # elif faculty_id:
    #     if semester_id:
    #     if days_id:
    #         pass
    #     elif time_period_id:
    #         pass
    #     elif building_id:
    #         pass
    #     elif room_id:
    #         pass
    #     elif course_name:
    #         pass
    #     else:
    #         pass
    # elif course_name:
    #     if faculty_id:
    #         pass
    #     elif days_id:
    #         pass
    #     elif time_period_id:
    #         pass
    #     elif building_id:
    #         pass
    #     elif room_id:
    #         pass
    #     elif semester_id:
    #         pass
    #     else:
    #         pass
    if department_id:
        section = Section.objects.filter(course_id__department_id_id=int(department_id))
        if department_id and faculty_id:
            section = Section.objects.filter(course_id__department_id_id=int(department_id), faculty_id_id=int(faculty_id))
        if department_id and building_id:
            print(building_id)
            print(department_id)
            section = Section.objects.filter(course_id__department_id_id=int(department_id), room_id__building_id_id=int(building_id))
            print("here")
        if department_id and room_id:
            section = Section.objects.filter(course_id__department_id_id=int(department_id), room_id_id=int(room_id))
            # print("here")
        if department_id and semester_id:
            section = Section.objects.filter(course_id__department_id_id=int(department_id), semester_id_id=int(semester_id))
        if department_id and faculty_id and semester_id:
            section = Section.objects.filter(course_id__department_id_id=int(department_id), faculty_id_id=int(faculty_id),
                                             semester_id_id=int(semester_id))
        if department_id and faculty_id and days_id:
            section = Section.objects.filter(course_id__department_id_id=int(department_id), faculty_id_id=int(faculty_id),
                                             time_slot_id__days_id_id=int(days_id))
        if department_id and faculty_id and time_period_id:
            section = Section.objects.filter(course_id__department_id_id=int(department_id), faculty_id_id=int(faculty_id),
                                             time_slot_id__period_id_id=int(time_period_id))
        if department_id and faculty_id and building_id:
            section = Section.objects.filter(course_id__department_id_id=int(department_id), faculty_id_id=int(faculty_id),
                                             room_id__building_id_id=int(building_id))
        if department_id and faculty_id and room_id:
            section = Section.objects.filter(course_id__department_id_id=int(department_id), faculty_id_id=int(faculty_id),
                                             room_id_id=int(room_id))
    elif faculty_id:
        section = Section.objects.filter(faculty_id_id=int(faculty_id))
        if faculty_id and semester_id:
            section = Section.objects.filter(faculty_id_id=int(faculty_id), semester_id_id=int(semester_id))
        if faculty_id and days_id:
            section = Section.objects.filter(faculty_id_id=int(faculty_id), time_slot_id__days_id_id=int(days_id))
        if faculty_id and time_period_id:
            section = Section.objects.filter(faculty_id_id=int(faculty_id), time_slot_id__period_id_id=int(time_period_id))
        if faculty_id and semester_id and days_id:
            section = Section.objects.filter(faculty_id_id=int(faculty_id), semester_id_id=int(semester_id),
                                             time_slot_id__days_id_id=int(days_id))
        if faculty_id and semester_id and time_period_id:
            section = Section.objects.filter(faculty_id_id=int(faculty_id), semester_id_id=int(semester_id),
                                             time_slot_id__period_id_id=int(time_period_id))
    elif days_id:
        section = Section.objects.filter(time_slot_id__days_id_id=int(days_id))
        if days_id and time_period_id:
            section = Section.objects.filter(time_slot_id__days_id_id=int(days_id),
                                             time_slot_id__period_id_id=int(time_period_id))
        if days_id and semester_id:
            section = Section.objects.filter(time_slot_id__days_id_id=int(days_id), semester_id_id=int(semester_id))
    elif time_period_id:
        section = Section.objects.filter(time_slot_id__period_id_id=int(time_period_id))
        if time_period_id and semester_id:
            section = Section.objects.filter(time_slot_id__period_id_id=int(time_period_id), semester_id_id=int(semester_id))
    elif building_id:
        section = Section.objects.filter( room_id__building_id_id=int(building_id))
        if building_id and room_id:
            section = Section.objects.filter( room_id__building_id_id=int(building_id), room_id_id=int(room_id))
        if building_id and room_id and semester_id:
            section = Section.objects.filter( room_id__building_id_id=int(building_id),
                                             room_id_id=int(room_id), semester_id_id=int(semester_id))
        if building_id and semester_id:
            section = Section.objects.filter( room_id__building_id_id=int(building_id),
                                             semester_id_id=int(semester_id))
    elif room_id:
        section = Section.objects.filter(room_id_id=int(room_id))
        if room_id and semester_id:
            section = Section.objects.filter(room_id_id=int(room_id), semester_id_id=int(semester_id))
    elif course_name:
        section = Section.objects.filter(course_id__name__contains=course_name)
        if course_name and semester_id:
            section = Section.objects.filter(course_id__name__contains=course_name, semester_id_id=semester_id)
    elif semester_id:
        section = Section.objects.filter(semester_id_id=int(semester_id))

    for s in section:
        faculty = Faculty.objects.get(pk=int(s.faculty_id_id))
        faculty_name = faculty.faculty_id.user.first_name + ' ' + faculty.faculty_id.user.last_name
        prerequisites = Prerequisite.objects.filter(course_id=s.course_id)
        prereq_array = []
        for p in prerequisites:
            prereq_array.append({
                'name': p.course_required_id.name
            })
        data = {
            'faculty': faculty_name,
            'course_name': s.course_id.name,
            'course_description': s.course_id.description,
            'department': s.course_id.department_id.name,
            'semester_year': s.semester_id.year,
            'semester_season': s.semester_id.season,
            'semester_status': s.semester_id.status,
            'section_id': s.section_id,
            'credits' : s.course_id.credits,
            'seats_taken': s.seats_taken,
            'capacity': s.room_id.capacity,
            'meeting_days': s.time_slot_id.days_id.day_1 + ' ' + s.time_slot_id.days_id.day_2,
            'time_period': s.time_slot_id.period_id.start_time.strftime('%H:%M %p') + '-'
                           + s.time_slot_id.period_id.end_time.strftime('%H:%M %p'),
            'room': s.room_id.room_number,
            'building': s.room_id.building_id.name,
            'prerequisites': prereq_array
        }
        schedule_data.append(data)

    return HttpResponse(json.dumps(schedule_data), content_type="application/json")
