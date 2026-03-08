# apps/academic/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register("subjects", SubjectViewSet, basename="subjects")
router.register("timeslots", TimeSlotViewSet, basename="timeslots")



urlpatterns = [
    path('', include(router.urls)),

    # Principal URLs
    path('principal/dashboard/', PrincipalDashboardView.as_view(), name='principal-dashboard'),
    path('principal/assign-class-teacher/', AssignClassTeacherView.as_view(), name='assign-class-teacher'),
    path('principal/teachers/', ListTeachersView.as_view(), name='list-teachers'),
    path("principal/class-teachers/",ClassTeacherListView.as_view(),),
    path("principal/class-teachers/<int:pk>/",ClassTeacherDeleteView.as_view(),),
    path('principal/timetable/bulk-create/', BulkTimetableCreate.as_view(), name='bulk-create-timetable'),
    path('principal/timetable/', get_class_timetable, name='get-class-timetable'),
    path('principal/timetable/class/<int:classroom_id>/', ClassTimetableView.as_view(), name='class-timetable'),
    path('principal/timetable/delete/<int:classroom_id>/', delete_class_timetable, name='delete-class-timetable'),
    
    # Teacher URLs
    path('teacher/dashboard/', TeacherDashboardView.as_view(), name='teacher-dashboard'),
    path('teacher/all-students/', TeacherAllStudentsView.as_view(), name='teacher-all-students'),
    path('teacher/today-classes/', TeacherTodayClassesView.as_view(), name='teacher-today-classes'),
    path('teacher/take-attendance/<int:timetable_id>/', TakeAttendanceView.as_view(), name='take-attendance'),
    path('teacher/class-attendance/<int:classroom_id>/', ClassTeacherAttendanceView.as_view(), name='class-attendance'),
    path('teacher/class-attendance/<int:classroom_id>/<str:date>/', ClassTeacherAttendanceView.as_view(), name='class-attendance-date'),

    # Class Teacher URLs
    path("teacher/my-class/students/",ClassTeacherStudentsView.as_view(),name="class-teacher-students"),
    path("teacher/student-subject-attendance/<int:student_id>/",TeacherStudentSubjectAttendanceView.as_view(),name="teacher-student-subject-attendance"),
    
    # Student URLs
    path('student/dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
    path('student/today-classes/', StudentTodayClassesView.as_view(), name='student-today-classes'),
    
    # Parent URLs
    path('parent/dashboard/', ParentDashboardView.as_view(), name='parent-dashboard'),
    path('parent/child-attendance/<int:student_id>/', ChildAttendanceView.as_view(), name='child-attendance'),
]

