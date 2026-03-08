from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import IntegerField
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from django.db.models.functions import Cast
from rest_framework.response import Response
from .models import ClassRoom, calculate_grade
from .models import Exam, SubjectExam, StudentMark, ClassSubject
from apps.students.models import Student
from apps.academic.models import ClassTeacher, Subject
from utils.permissions import IsPrincipal
from .serializers import (
    ExamSerializer,
    SubjectExamSerializer,
    StudentMarkSerializer,
    ClassroomSerializer,
    ClassSubjectSerializer
)



class ClassRoomListView(generics.ListAPIView):
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ClassRoom.objects.annotate(
            class_number=Cast("class_name", IntegerField())
        ).order_by("class_number", "section")
    
class ClassRoomDetailView(generics.RetrieveAPIView):
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticated]
    queryset = ClassRoom.objects.all()
    
class ExamViewSet(ModelViewSet):

    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]


class SubjectExamViewSet(ModelViewSet):

    queryset = SubjectExam.objects.all()
    serializer_class = SubjectExamSerializer
    permission_classes = [IsAuthenticated, IsPrincipal]


class StudentMarkViewSet(ModelViewSet):
    serializer_class = StudentMarkSerializer
    permission_classes = [IsAuthenticated]

    queryset = StudentMark.objects.select_related(
        "student",
        "subject_exam",
        "subject_exam__subject",
        "subject_exam__exam"
    )
    
    def get_queryset(self):

        queryset = super().get_queryset()

        student_id = self.request.query_params.get("student")

        if student_id:
            queryset = queryset.filter(student_id=student_id)

        return queryset

    
    
class GenerateReportCard(APIView):

    def get(self, request, student_id):

        student = Student.objects.get(id=student_id)

        marks = StudentMark.objects.filter(
            student=student
        ).select_related(
            "subject_exam__exam"
        )

        total_weighted_marks = 0
        total_weightage = 0

        for mark in marks:

            exam = mark.subject_exam.exam
            weight = exam.weightage

            percentage = (
                mark.marks_obtained /
                mark.subject_exam.total_marks
            ) * 100

            weighted_score = percentage * (weight / 100)

            total_weighted_marks += weighted_score
            total_weightage += weight

        final_percentage = total_weighted_marks

        grade = calculate_grade(final_percentage)

        return Response({

            "student": student.user.first_name,
            "percentage": round(final_percentage, 2),
            "grade": grade

        })
        
class ClassTeacherStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        teacher = request.user.teacher_profile

        class_teacher = ClassTeacher.objects.filter(
            teacher=teacher
        ).select_related("classroom").first()

        if not class_teacher:
            return Response({"detail": "Not class teacher"}, status=403)

        students = Student.objects.filter(
            classroom=class_teacher.classroom
        ).select_related("user")

        data = []

        for s in students:
            data.append({
                "id": s.id,
                "name": f"{s.user.first_name} {s.user.last_name}",
                "admission_number": s.admission_number
            })

        return Response({
            "classroom": str(class_teacher.classroom),
            "students": data
        })
        
class StudentMarkViewSet(ModelViewSet):

    queryset = StudentMark.objects.select_related(
        "student",
        "subject_exam",
        "subject_exam__subject"
    )

    serializer_class = StudentMarkSerializer
    
    # marks overview for class teacher
    @action(detail=False, methods=["get"], url_path="marks-overview")
    def marks_overview(self, request):

        teacher_profile = request.user.teacher_profile
        class_teacher = teacher_profile.class_teacher_of.select_related("classroom").first()

        if not class_teacher:
            return Response({"error": "Teacher is not assigned to any class"})

        classroom = class_teacher.classroom
        class_name = classroom.class_name
        section = classroom.section

        students = Student.objects.filter(
            classroom__class_name=class_name,
            classroom__section=section
        ).select_related("user").order_by("user__first_name","user__last_name")

        subject_exams = SubjectExam.objects.filter(
            exam__class_name=class_name
        ).select_related("subject")

        subjects = [se.subject.name for se in subject_exams]

        latest_exam = Exam.objects.filter(
            class_name=class_name
        ).order_by("-start_date").first()

        # preload marks to avoid N+1 queries
        marks_qs = StudentMark.objects.filter(
            student__in=students,
            subject_exam__in=subject_exams
        ).select_related("subject_exam")

        marks_map = {
            (m.student_id, m.subject_exam_id): m.marks_obtained
            for m in marks_qs
        }

        data = []

        for student in students:

            marks = {}

            for se in subject_exams:

                marks[se.subject.name] = marks_map.get(
                    (student.id, se.id)
                )

            data.append({
                "id": student.id,
                "name": f"{student.user.first_name} {student.user.last_name}",
                "admission_number": student.admission_number,
                "photo": student.photo.url if student.photo else None,
                "marks": marks
            })

        return Response({
            "students": data,
            "subjects": subjects,
            "exam": latest_exam.name if latest_exam else None,
            "exams": Exam.objects.filter(class_name=class_name).values("id","name")
        })


    # -------- ENTER / UPDATE MARKS (BULK) --------
    @action(detail=False, methods=["post"], url_path="enter-marks")
    def enter_marks(self, request):

        subject_exam_id = request.data.get("subject_exam")
        marks_data = request.data.get("marks", [])

        if not subject_exam_id:
            return Response(
                {"error": "subject_exam is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            subject_exam = SubjectExam.objects.get(id=subject_exam_id)
        except SubjectExam.DoesNotExist:
            return Response(
                {"error": "Invalid subject_exam"},
                status=status.HTTP_404_NOT_FOUND
            )

        saved_marks = []

        for m in marks_data:

            obj, _ = StudentMark.objects.update_or_create(
                student_id=m["student_id"],
                subject_exam=subject_exam,
                defaults={
                    "marks_obtained": m.get("marks", 0)
                }
            )

            saved_marks.append(obj.id)

        return Response({
            "detail": "Marks saved successfully",
            "records_updated": len(saved_marks)
        })


    # -------- FILTER MARKS --------
    def get_queryset(self):

        queryset = super().get_queryset()

        subject_exam = self.request.query_params.get("subject_exam")
        student = self.request.query_params.get("student")

        if subject_exam:
            queryset = queryset.filter(subject_exam_id=subject_exam)

        if student:
            queryset = queryset.filter(student_id=student)

        return queryset
    
# class ClassTeacherMarksOverview(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):

#         teacher = request.user.teacher_profile

#         class_teacher = ClassTeacher.objects.select_related("classroom").filter(
#             teacher=teacher
#         ).first()

#         if not class_teacher:
#             return Response({"detail": "Not class teacher"}, status=403)

#         classroom = class_teacher.classroom

#         students = Student.objects.filter(
#             classroom=classroom
#         ).select_related("user")

#         subject_exams = SubjectExam.objects.filter(
#             exam__class_name=classroom.split("-")[0]
#         ).select_related("subject")

#         subjects = [se.subject.name for se in subject_exams]

#         exams = Exam.objects.filter(classroom=classroom)

#         latest_exam = exams.order_by("-id").first()

#         data = []

#         for s in students:

#             subject_marks = {}

#             for sub in subjects:

#                 mark = StudentMark.objects.filter(
#                     student=s,
#                     subject_exam__subject=sub,
#                     subject_exam__exam=latest_exam
#                 ).first()

#                 subject_marks[sub.name] = mark.marks_obtained if mark else None

#             data.append({
#                 "id": s.id,
#                 "name": f"{s.user.first_name} {s.user.last_name}",
#                 "admission_number": s.admission_number,
#                 "photo": s.photo.url if s.photo else None,
#                 "marks": subject_marks
#             })

#         return Response({
#             "exam": latest_exam.name if latest_exam else None,
#             "subjects": [s.name for s in subjects],
#             "students": data
#         })
        
class CreateExamView(APIView):

    permission_classes = [IsAuthenticated, IsPrincipal]

    def post(self, request):

        class_name = request.data.get("class_name")
        name = request.data.get("name")
        academic_year = request.data.get("academic_year")
        weightage = request.data.get("weightage")
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")

        # classroom = ClassRoom.objects.get(id=classroom_id)

        exam = Exam.objects.create(
            name=name,
            class_name=class_name,
            academic_year=academic_year,
            weightage=weightage,
            start_date=start_date,
            end_date=end_date
        )

        return Response({
            "detail": "Exam created",
            "exam": ExamSerializer(exam).data
        })

class SubjectExamViewSet(ModelViewSet):

    queryset = SubjectExam.objects.select_related(
        "exam",
        "subject"
    )

    serializer_class = SubjectExamSerializer
    permission_classes = [IsAuthenticated]
class ClassSubjectViewSet(ModelViewSet):

    queryset = ClassSubject.objects.select_related(
        "classroom",
        "subject"
    )

    serializer_class = ClassSubjectSerializer
    permission_classes = [IsAuthenticated, IsPrincipal]

    @action(detail=False, methods=["post"])
    def assign_subjects(self, request):

        classroom_id = request.data.get("classroom")
        subjects = request.data.get("subjects", [])

        created = []

        for subject_id in subjects:

            obj, _ = ClassSubject.objects.get_or_create(
                classroom_id=classroom_id,
                subject_id=subject_id
            )

            created.append(obj.subject.name)

        return Response({
            "detail": "Subjects assigned to class",
            "subjects": created
        })
         
class ClassSubjectsByClassView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, classroom_id):

        subjects = ClassSubject.objects.filter(
            classroom_id=classroom_id
        ).select_related("subject")

        data = []

        for s in subjects:
            data.append({
                "id": s.id,
                "subject_id": s.subject.id,
                "subject_name": s.subject.name,
                "is_exam_subject": s.is_exam_subject
            })

        return Response(data)
    
class BulkCreateExams(APIView):

    permission_classes = [IsAuthenticated, IsPrincipal]

    def post(self, request):

        name = request.data.get("name")
        weightage = request.data.get("weightage")
        academic_year = request.data.get("academic_year")
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")

        classes = ClassRoom.objects.values_list("class_name", flat=True).distinct()

        for c in classes:

            Exam.objects.get_or_create(
                class_name=c,
                name=name,
                academic_year=academic_year,
                defaults={
                    "weightage": weightage,
                    "start_date":start_date,
                    "end_date":end_date
                }
            )
            

        return Response({"detail":"Exam created for all classes"})
    
class DeleteExamView(APIView):

    permission_classes = [IsAuthenticated, IsPrincipal]

    def delete(self, request, exam_id):

        try:
            exam = Exam.objects.get(id=exam_id)

            exam.delete()

            return Response({
                "detail": "Exam deleted successfully"
            })

        except Exam.DoesNotExist:

            return Response({
                "detail": "Exam not found"
            }, status=404)
            
class DeleteExamTypeView(APIView):

    permission_classes = [IsAuthenticated, IsPrincipal]

    def delete(self, request, name):

        exams = Exam.objects.filter(name=name)

        count = exams.count()

        exams.delete()

        return Response({
            "detail": f"{name} deleted for all classes",
            "deleted_count": count
        })
        
class UpdateExamTypeView(APIView):

    permission_classes = [IsAuthenticated, IsPrincipal]

    def put(self, request, name):

        weightage = request.data.get("weightage")
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")

        exams = Exam.objects.filter(name=name)

        update_data = {}

        if weightage not in [None, ""]:
            update_data["weightage"] = float(weightage)

        if start_date:
            update_data["start_date"] = start_date

        if end_date:
            update_data["end_date"] = end_date

        exams.update(**update_data)

        return Response({
            "detail": f"{name} updated for all classes"
        })
        
class UpdateSingleExamView(APIView):

    permission_classes = [IsAuthenticated, IsPrincipal]

    def put(self, request, exam_id):

        try:

            exam = Exam.objects.get(id=exam_id)

            weightage = request.data.get("weightage")
            start_date = request.data.get("start_date")
            end_date = request.data.get("end_date")

            if weightage not in [None, ""]:
                exam.weightage = float(weightage)

            if start_date:
                exam.start_date = start_date

            if end_date:
                exam.end_date = end_date

            exam.save()

            return Response({
                "detail": "Exam updated",
                "exam_id": exam.id
            })

        except Exam.DoesNotExist:

            return Response({
                "detail": "Exam not found"
            }, status=404)