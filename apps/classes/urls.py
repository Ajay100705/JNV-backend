from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClassRoomListView, 
    ClassRoomDetailView,
    ExamViewSet,
    SubjectExamViewSet,
    StudentMarkViewSet,
    ClassSubjectViewSet,
    GenerateReportCard,
    ClassTeacherStudentsView,
    CreateExamView,
    ClassSubjectsByClassView,
    BulkCreateExams,
    DeleteExamView,
    UpdateExamTypeView,
    UpdateSingleExamView,
    DeleteExamTypeView,
    StudentMarkViewSet,
    
)

router = DefaultRouter()

router.register("exams", ExamViewSet, basename="exams")
router.register("exam-subjects", SubjectExamViewSet, basename="exam-subjects")
router.register("student-marks", StudentMarkViewSet, basename="student-marks")
router.register("class-subjects", ClassSubjectViewSet, basename="class-subjects")
# router.register("exam-subjects", SubjectExamViewSet, basename="exams-subjects")
router.register

urlpatterns = [
    path("", include(router.urls)),
    path('classrooms/', ClassRoomListView.as_view(), name='classroom-list'),
    path('classrooms/<int:pk>/', ClassRoomDetailView.as_view(), name='classroom-detail'),
    path('report-card/<int:student_id>/', GenerateReportCard.as_view(), name='report-card'),
    path('class-teacher-students/<int:classroom_id>/', ClassTeacherStudentsView.as_view(), name='class-teacher-students'),
        
    path('create-exam/', CreateExamView.as_view(), name='create-exam'),
    path('bulk-create-exams/', BulkCreateExams.as_view(), name='bulk-create-exams'),
    
    path('delete-exam/<int:exam_id>/', DeleteExamView.as_view(), name='delete-exam'),
    path('delete-exam-type/<str:name>/', DeleteExamTypeView.as_view(), name='delete-exam-type'),
    
    path('update-exam-type/<str:name>/', UpdateExamTypeView.as_view(), name='update-exam-type'),
    path('update-single-exam/<int:exam_id>/', UpdateSingleExamView.as_view(), name='update-single-exam'),
    
    path('class-subjects/<int:classroom_id>/', ClassSubjectsByClassView.as_view(), name='class-subjects-by-class')

]
