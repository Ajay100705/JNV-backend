# apps/academic/views.py
from urllib import request

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from django.utils import timezone
from datetime import datetime, time
from django.db.models import Count, Q
from .models import Subject, ClassTeacher, TeacherSubject, TimeSlot, Timetable, Attendance, TeacherUnavailable
from .serializers import *
from .utils import get_current_academic_year
from apps.students.models import Student
from apps.teachers.models import TeacherProfile
from apps.classes.models import ClassRoom
from utils.permissions import IsPrincipal, IsTeacher,IsTeacherOrPrincipal, IsParent, IsStudent
from rest_framework.permissions import IsAuthenticated

class CanMarkAttendance(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Teachers can mark attendance
        if request.user.role == 'teacher':
            return True
        
        # Principal can mark any attendance
        if request.user.role == 'principal':
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # For timetable objects
        if isinstance(obj, Timetable):
            # Principal can access any
            if request.user.role == 'principal':
                return True
            
            # Teachers can only access their subjects
            if request.user.role == 'teacher':
                teacher = request.user.teacher_profile
                
                # Check if teacher is class teacher of this class
                try:
                    class_teacher = ClassTeacher.objects.get(
                        classroom=obj.classroom,
                        academic_year=obj.academic_year
                    )
                    if class_teacher.teacher == teacher:
                        return True
                except ClassTeacher.DoesNotExist:
                    pass
                
                # Check if teacher teaches this subject in this class
                return TeacherSubject.objects.filter(
                    teacher=teacher,
                    subject=obj.subject,
                    classroom=obj.classroom
                ).exists()
            
            return False
        
        return True

# Principal Views
class PrincipalDashboardView(APIView):
    permission_classes = [IsPrincipal]
    
    def get(self, request):
        total_students = Student.objects.count()
        total_teachers = TeacherProfile.objects.count()
        total_classes = ClassRoom.objects.count()
        today_attendance = Attendance.objects.filter(date=timezone.now().date()).count()
        academic_year = get_current_academic_year()
        # Classes without class teachers
        classes_without_teacher = ClassRoom.objects.exclude(
            id__in=ClassTeacher.objects.filter(
                academic_year=academic_year
            ).values_list('classroom_id', flat=True)
        ).count()
        
        data = {
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_classes': total_classes,
            'today_attendance': today_attendance,
            'classes_without_teacher': classes_without_teacher,
        }
        return Response(data)

class AssignClassTeacherView(generics.CreateAPIView):
    permission_classes = [IsPrincipal]
    serializer_class = ClassTeacherSerializer
    queryset = ClassTeacher.objects.all()

class ListTeachersView(generics.ListAPIView):
    permission_classes = [IsPrincipal]
    queryset = TeacherProfile.objects.all()
    serializer_class = serializers.ModelSerializer  # You'll need to create this

    def get_serializer_class(self):
        from apps.teachers.serializers import TeacherProfileSerializer
        return TeacherProfileSerializer
    
class ClassTeacherListView(generics.ListAPIView):
    permission_classes = [IsPrincipal]
    queryset = ClassTeacher.objects.select_related("teacher", "classroom")
    serializer_class = ClassTeacherSerializer

class ClassTeacherDeleteView(generics.DestroyAPIView):
    permission_classes = [IsPrincipal]
    queryset = ClassTeacher.objects.all()
    serializer_class = ClassTeacherSerializer

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all().order_by("name")
    serializer_class = SubjectSerializer

class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all().order_by("period_number")
    serializer_class = TimeSlotSerializer
class BulkTimetableCreate(APIView):

    permission_classes=[IsPrincipal]

    def post(self, request):

        errors = []

        for row in request.data:

            classroom = row["classroom"]
            day = row["day"]
            time_slot = row["time_slot"]
            teacher = row["teacher"]
            subject = row["subject"]

            # ❌ Same class same period
            class_conflict = Timetable.objects.filter(
                classroom_id=classroom,
                day=day,
                time_slot_id=time_slot
            ).exclude(
                subject_id=subject
            ).first()

            if class_conflict:
                errors.append(
                    f"Class already has subject in {day} period {time_slot}"
                )
                continue

            # ❌ Same teacher same period
            teacher_conflict = Timetable.objects.filter(
                teacher_id=teacher,
                day=day,
                time_slot_id=time_slot
            ).exclude(
                classroom_id=classroom
            ).first()

            if teacher_conflict:
                errors.append(
                    f"Teacher already assigned in {day} period {time_slot}"
                )
                continue

            # ❌ Teacher unavailable slot
            unavailable = TeacherUnavailable.objects.filter(
                teacher_id=teacher,
                day=day,
                time_slot_id=time_slot
            ).exists()

            if unavailable:
                errors.append(
                    f"Teacher unavailable in {day} period {time_slot}"
                )
                continue

            Timetable.objects.update_or_create(
                classroom_id=classroom,
                day=day,
                time_slot_id=time_slot,
                defaults={
                    "subject_id": subject,
                    "teacher_id": teacher,
                    "academic_year": get_current_academic_year(),
                    "is_active": True
                }
            )

        if errors:
            return Response(
                {"errors": errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"message": "Timetable saved"})
    
@api_view(["GET"])
def get_class_timetable(request):
    classroom_id = request.GET.get("classroom")

    queryset = Timetable.objects.filter(classroom_id=classroom_id)\
        .select_related("subject", "teacher", "time_slot", "classroom")\

    serializer = TimetableSerializer(queryset, many=True)

    return Response(serializer.data)

@api_view(["DELETE"])
def delete_class_timetable(request, classroom_id):

    Timetable.objects.filter(
        classroom_id=classroom_id
    ).delete()

    return Response({"message": "Timetable deleted"})

class ClassTimetableView(generics.ListAPIView):
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        classroom_id = self.kwargs.get("classroom_id")

        queryset = Timetable.objects.filter(classroom_id=classroom_id).select_related(
            "subject",
            "teacher",
            "time_slot",
            "classroom"
        )

        if classroom_id:
            queryset = queryset.filter(classroom_id=classroom_id)

        return queryset

# Class Teacher Views
# class TeacherMyClassStudentsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         if request.user.role != "teacher":
#             return Response({"detail": "Only teachers allowed"}, status=403)

#         teacher = request.user.teacher_profile

#         # Get current academic year
#         now = timezone.now()
#         year = now.year
#         month = now.month

#         if month < 4:
#             academic_year = f"{year - 1}-{str(year)[-2:]}"
#         else:
#             academic_year = f"{year}-{str(year + 1)[-2:]}"

#         class_teacher = ClassTeacher.objects.filter(
#             teacher=teacher,
#             academic_year=academic_year
#         ).select_related("classroom").first()

#         if not class_teacher:
#             return Response(
#                 {"detail": "You are not assigned as class teacher."},
#                 status=403
#             )

#         students = Student.objects.filter(
#             classroom=class_teacher.classroom
#         ).select_related("user", "house")

#         data = [
#             {
#                 "id": s.id,
#                 "name": s.user.get_full_name(),
#                 "admission_number": s.admission_number,
#                 "gender": s.user.gender,
#                 "house_name": s.house.house_name if s.house else None,
#             }
#             for s in students
#         ]

#         return Response(data)

# Teacher Views
class TeacherDashboardView(APIView):
    permission_classes = [IsTeacher]
    
    def get(self, request):
        teacher = request.user.teacher_profile
        
        # Get today's classes for this teacher
        today = timezone.now().date()
        day_name = today.strftime('%a').upper()[:3]
        
        today_classes = Timetable.objects.filter(
            teacher=teacher,
            day=day_name,
            is_active=True
        ).select_related('classroom', 'subject', 'time_slot')
        
        completed_classes = 0
        classes_data = []
        for class_info in today_classes:
            attendance_taken = Attendance.objects.filter(
                timetable=class_info,
                date=today
            ).exists()

            if attendance_taken:
                completed_classes += 1
            
            classes_data.append({
                'id': class_info.id,
                'classroom': str(class_info.classroom),
                'subject': class_info.subject.name,
                'period': class_info.time_slot.period_number,
                'time': f"{class_info.time_slot.start_time} - {class_info.time_slot.end_time}",
                'attendance_taken': attendance_taken
            })

        # Classes today
        classes_today_count = today_classes.count()
        pending_attendance = classes_today_count - completed_classes

        # Total students across teacher classes
        # classrooms = today_classes.values_list("classroom", flat=True).distinct()
        # print("Classrooms today:", classrooms)

        teacher = request.user.teacher_profile

        classrooms = Timetable.objects.filter(
            teacher=teacher
        ).values_list("classroom", flat=True).distinct()

        class_data = (
            Student.objects
            .filter(classroom__in=classrooms)
            .values("classroom__class_name", "classroom__section")
            .annotate(total_students=Count("id"))
        )

        class_strength = [
            {
                "class_name": f"{item['classroom__class_name']}{item['classroom__section']}",
                "students": item["total_students"]
            }
            for item in class_data
        ]

        total_students = sum(item['students'] for item in class_strength)
        total_classes = len(class_strength)

        # total_students = Student.objects.filter(
        #     classroom__in=classrooms
        # ).count()

        # print("Total students in today's classes:", total_students)

        # Attendance rate today
        attendance_today = Attendance.objects.filter(
            timetable__teacher=teacher,
            date=today
        )

        total_attendance = attendance_today.count()
        present_count = attendance_today.filter(status="PRESENT").count()

        attendance_percentage = 0
        if total_attendance > 0:
            attendance_percentage = round((present_count / total_attendance) * 100)

        
        # Check if teacher is class teacher
        try:
            class_teacher_of = ClassTeacher.objects.get(
                teacher=teacher,
                academic_year=get_current_academic_year()
            )
            is_class_teacher = True
            my_class = str(class_teacher_of.classroom)
        except ClassTeacher.DoesNotExist:
            is_class_teacher = False
            my_class = None
        
        data = {
            'teacher_name': str(teacher),
            'is_class_teacher': is_class_teacher,
            'my_class': my_class,

            'totalStudents': total_students,
            'totalClasses': total_classes,
            'classStrength': class_strength,

            
            'classesToday': classes_today_count,
            'classesCompleted': completed_classes,
            'attendance_percentage': attendance_percentage,
            'pendingAssessment': 0,  # Add later when assessments are implemented

            'today_classes': classes_data,
        }
        return Response(data)
    
# All Students of that teacher he teatches 
class TeacherAllStudentsView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        teacher = request.user.teacher_profile

        # All timetables of this teacher
        timetables = Timetable.objects.filter(
            teacher=teacher,
            is_active=True
        )

        timetable_ids = timetables.values_list("id", flat=True)

        classrooms = timetables.values_list("classroom", flat=True).distinct()

        students = Student.objects.filter(
            classroom__in=classrooms
        ).select_related("user", "house", "parent")

        data = []

        for s in students:

            attendance = Attendance.objects.filter(
                student=s,
                timetable_id__in=timetable_ids
            )

            total_classes = attendance.count()

            present = attendance.filter(status="PRESENT").count()
            absent = attendance.filter(status="ABSENT").count()
            leave = attendance.filter(status="LEAVE").count()

            percentage = 0
            if total_classes > 0:
                percentage = round((present / total_classes) * 100, 1)

            data.append({
                "id": s.id,
                "name": f"{s.user.first_name} {s.user.last_name}",
                "admission_number": s.admission_number,
                "gender": s.user.gender,
                "photo": s.photo.url if s.photo else None,

                "classroom": str(s.classroom),

                "house_name": s.house.house_name if s.house else None,
                "house_category": s.house.house_category if s.house else None,

                "parent_name": str(s.parent) if s.parent else None,
                "parent_phone1": s.parent.phone1 if s.parent else None,
                "parent_phone2": s.parent.phone2 if s.parent else None,
                "parent_email": s.parent.email if s.parent else None,
                "parent_photo": s.parent.photo.url if s.parent and s.parent.photo else None,
                "parent_job": s.parent.job if s.parent else None,
                "parent_present_address": s.parent.present_address if s.parent else None,
                "parent_permanent_address": s.parent.permanent_address if s.parent else None,

                # Attendance stats
                "total_classes": total_classes,
                "present": present,
                "absent": absent,
                "leave": leave,
                "attendance_percentage": percentage,
            })

            print(data)

        return Response({"students": data})


class TeacherTodayClassesView(APIView):
    permission_classes = [IsTeacher]
    
    def get(self, request):
        teacher = request.user.teacher_profile
        today = timezone.now().date()
        day_name = today.strftime('%a').upper()[:3]
        
        today_classes = Timetable.objects.filter(
            teacher=teacher,
            day=day_name,
            is_active=True
        ).order_by('time_slot__period_number')
        
        data = []

        for t in today_classes:
            attendance_taken = Attendance.objects.filter(
                timetable=t,
                date=timezone.now().date()
            ).exists()

            data.append({
                "id": t.id,
                "subject": t.subject.name,
                "classroom": str(t.classroom),
                "period": t.time_slot.period_number,
                "time": f"{t.time_slot.start_time.strftime('%H:%M')} - {t.time_slot.end_time.strftime('%H:%M')}",
                "attendance_taken": attendance_taken
            })

        return Response(data)

class TakeAttendanceView(APIView):
    permission_classes = [IsAuthenticated,CanMarkAttendance]
    
    
    def get(self, request, timetable_id):

        teacher = request.user.teacher_profile
        timetable = get_object_or_404(Timetable, id=timetable_id)

        # SUBJECT TEACHER
        if timetable.teacher_id == teacher.id:
            allowed = True

        # CLASS TEACHER OVERRIDE
        elif ClassTeacher.objects.filter(
            teacher=teacher,
            classroom=timetable.classroom,
            academic_year=get_current_academic_year()
        ).exists():
            allowed = True

        else:
            allowed = False

        if not allowed:
            return Response(
                {"error": "You are not allowed to mark attendance"},
                status=403
            )

        date = request.query_params.get("date", timezone.now().date())

        students = Student.objects.filter(
            classroom=timetable.classroom
        ).order_by("user__first_name")

        existing_attendance = Attendance.objects.filter(
            timetable=timetable,
            date=date
        ).select_related("student")

        attendance_map = {att.student_id: att for att in existing_attendance}

        students_data = []

        for student in students:
            att = attendance_map.get(student.id)

            students_data.append({
                "student_id": student.id,
                "student_name": str(student),
                "admission_number": student.admission_number,
                "status": att.status if att else None,
                "attendance_id": att.id if att else None
            })

        return Response({
            "timetable": TimetableSerializer(timetable).data,
            "date": date,
            "students": students_data
        })
    
    def post(self, request, timetable_id):

        teacher = request.user.teacher_profile
        timetable = get_object_or_404(Timetable, id=timetable_id)

        # SUBJECT TEACHER
        if timetable.teacher_id == teacher.id:
            allowed = True

        # CLASS TEACHER OVERRIDE
        elif ClassTeacher.objects.filter(
            teacher=teacher,
            classroom=timetable.classroom,
            academic_year=get_current_academic_year()
        ).exists():
            allowed = True

        else:
            allowed = False

        if not allowed:
            return Response(
                {"error": "You are not allowed to mark attendance"},
                status=403
            )

        serializer = BulkAttendanceSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        date = serializer.validated_data["date"]
        attendance_data = serializer.validated_data["attendance_data"]

        created_count = 0
        updated_count = 0

        for att_data in attendance_data:

            student_id = att_data["student_id"]
            status = att_data["status"]
            remarks = att_data.get("remarks", "")

            attendance, created = Attendance.objects.update_or_create(
                student_id=student_id,
                timetable=timetable,
                date=date,
                defaults={
                    "status": status,
                    "marked_by": teacher,
                    "remarks": remarks
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        return Response({
            "message": "Attendance saved successfully",
            "created": created_count,
            "updated": updated_count
        })


class ClassTeacherAttendanceView(APIView):
    permission_classes = [IsTeacher]
    
    def get(self, request, classroom_id, date=None):
        teacher = request.user.teacher_profile
        
        # Check if teacher is class teacher of this class
        try:
            class_teacher = ClassTeacher.objects.get(
                classroom_id=classroom_id,
                academic_year=get_current_academic_year()
            )
            if class_teacher.teacher != teacher:
                return Response({'error': 'You are not the class teacher'}, status=403)
        except ClassTeacher.DoesNotExist:
            return Response({'error': 'Class teacher not found'}, status=404)
        
        if not date:
            date = timezone.now().date()
        
        # Get all timetables for this class on this day
        day_name = date.strftime('%a').upper()[:3]
        timetables = Timetable.objects.filter(
            classroom_id=classroom_id,
            day=day_name,
            is_active=True
        ).select_related('subject', 'teacher')
        
        result = []
        for tt in timetables:
            attendance = Attendance.objects.filter(
                timetable=tt,
                date=date
            ).select_related('student')
            
            attendance_data = [
                {
                    'student_id': att.student_id,
                    'student_name': str(att.student),
                    'status': att.status
                }
                for att in attendance
            ]
            
            result.append({
                'period': tt.time_slot.period_number,
                'subject': tt.subject.name,
                'teacher': str(tt.teacher),
                'attendance': attendance_data,
                'total_students': Student.objects.filter(classroom_id=classroom_id).count(),
                'present_count': attendance.filter(status='PRESENT').count()
            })
        
        return Response(result)

# Student Views
class StudentDashboardView(APIView):
    permission_classes = [IsStudent]
    
    def get(self, request):
        student = request.user.student_profile
        today = timezone.now().date()
        day_name = today.strftime('%a').upper()[:3]
        
        # Get today's timetable
        today_classes = Timetable.objects.filter(
            classroom=student.classroom,
            day=day_name,
            is_active=True
        ).order_by('time_slot__period_number')
        
        classes_data = []
        for tt in today_classes:
            try:
                attendance = Attendance.objects.get(
                    student=student,
                    timetable=tt,
                    date=today
                )
                status = attendance.status
                status_color = 'green' if status == 'PRESENT' else 'red'
            except Attendance.DoesNotExist:
                status = None
                status_color = 'gray'
            
            classes_data.append({
                'period': tt.time_slot.period_number,
                'subject': tt.subject.name,
                'teacher': str(tt.teacher),
                'time': f"{tt.time_slot.start_time} - {tt.time_slot.end_time}",
                'status': status,
                'status_color': status_color
            })
        
        data = {
            'student_name': str(student),
            'classroom': str(student.classroom),
            'admission_number': student.admission_number,
            'today_classes': classes_data
        }
        return Response(data)

class StudentTodayClassesView(APIView):
    permission_classes = [IsStudent]
    
    def get(self, request):
        student = request.user.student_profile
        today = timezone.now().date()
        day_name = today.strftime('%a').upper()[:3]
        
        today_classes = Timetable.objects.filter(
            classroom=student.classroom,
            time_slot__day=day_name,
            is_active=True
        ).order_by('time_slot__period_number')
        
        result = []
        for tt in today_classes:
            try:
                attendance = Attendance.objects.get(
                    student=student,
                    timetable=tt,
                    date=today
                )
                status = attendance.status
            except Attendance.DoesNotExist:
                status = None
            
            result.append({
                'period': tt.time_slot.period_number,
                'subject': tt.subject.name,
                'teacher': str(tt.teacher),
                'time': f"{tt.time_slot.start_time} - {tt.time_slot.end_time}",
                'status': status
            })
        
        return Response(result)

# Parent Views
class ParentDashboardView(APIView):
    permission_classes = [IsParent]
    
    def get(self, request):
        parent = request.user.parent_profile
        children = parent.children.all()
        
        today = timezone.now().date()
        day_name = today.strftime('%a').upper()[:3]
        
        children_data = []
        for child in children:
            # Get today's classes for child
            today_classes = Timetable.objects.filter(
                classroom=child.classroom,
                time_slot__day=day_name,
                is_active=True
            ).order_by('time_slot__period_number')
            
            classes_data = []
            for tt in today_classes:
                try:
                    attendance = Attendance.objects.get(
                        student=child,
                        timetable=tt,
                        date=today
                    )
                    status = attendance.status
                except Attendance.DoesNotExist:
                    status = None
                
                classes_data.append({
                    'period': tt.time_slot.period_number,
                    'subject': tt.subject.name,
                    'status': status
                })
            
            children_data.append({
                'child_id': child.id,
                'child_name': str(child),
                'classroom': str(child.classroom),
                'today_attendance': classes_data,
                'overall_attendance_percentage': self.calculate_attendance(child)
            })
        
        return Response(children_data)
    
    def calculate_attendance(self, student):
        total_classes = Attendance.objects.filter(student=student).count()
        if total_classes == 0:
            return 0
        present_classes = Attendance.objects.filter(student=student, status='PRESENT').count()
        return round((present_classes / total_classes) * 100, 2)

class ChildAttendanceView(APIView):
    permission_classes = [IsParent]
    
    def get(self, request, student_id):
        parent = request.user.parent_profile
        
        try:
            child = Student.objects.get(id=student_id, parent=parent)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found or not your child'}, status=404)
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        attendance = Attendance.objects.filter(student=child)
        
        if start_date:
            attendance = attendance.filter(date__gte=start_date)
        if end_date:
            attendance = attendance.filter(date__lte=end_date)
        
        attendance = attendance.order_by('-date')
        serializer = AttendanceSerializer(attendance, many=True)
        
        return Response(serializer.data)
    

class ClassTeacherStudentsView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        teacher = request.user.teacher_profile

        # Get current academic year properly if you have util
        academic_year = get_current_academic_year()

        # Check if teacher is class teacher
        class_teacher = ClassTeacher.objects.filter(
            teacher=teacher,
            academic_year=academic_year
        ).select_related("classroom").first()

        if not class_teacher:
            return Response(
                {"detail": "You are not a class teacher."},
                status=403
            )

        classroom = class_teacher.classroom

        students = Student.objects.filter(
            classroom=classroom
        ).select_related("user", "parent", "house")

        result = []

        for student in students:

            total = Attendance.objects.filter(student=student).count()
            present = Attendance.objects.filter(
                student=student,
                status="PRESENT"
            ).count()

            percentage = round((present / total) * 100, 2) if total else 0

            result.append({
                "id": student.id,
                "name": str(student),
                "admission_number": student.admission_number,
                "gender": student.user.gender,
                "photo": student.photo.url if student.photo else None,
                
                "overall_attendance": percentage,
                "total_present": present,
                "total_classes": total,

                "house_name": student.house.house_name if student.house else None,
                "house_category": student.house.house_category if student.house else None,

                "classroom": str(student.classroom) if student.classroom else None,

                "parent_name": str(student.parent) if student.parent else None,
                "parent_phone1": student.parent.phone1 if student.parent else None,
                "parent_phone2": student.parent.phone2 if student.parent else None,
                "parent_email": student.parent.email if student.parent else None,
                "parent_photo": student.parent.photo.url if student.parent and student.parent.photo else None,
                "parent_job": student.parent.job if student.parent else None,
                "parent_present_address": student.parent.present_address if student.parent else None,
                "parent_permanent_address": student.parent.permanent_address if student.parent else None,
            })

        return Response({
            "classroom": str(classroom),
            "students": result
        })
    
class TeacherStudentSubjectAttendanceView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request, student_id):

        teacher = request.user.teacher_profile
        student = get_object_or_404(Student, id=student_id)

        # subjects teacher teaches to this student
        timetables = Timetable.objects.filter(
            teacher=teacher,
            classroom=student.classroom,
            is_active=True
        ).select_related("subject")

        subjects = timetables.values_list("subject", flat=True).distinct()

        result = []

        for subject_id in subjects:

            subject_name = timetables.filter(
                subject_id=subject_id
            ).first().subject.name

            attendance = Attendance.objects.filter(
                student=student,
                timetable__subject_id=subject_id
            )

            total = attendance.count()

            present = attendance.filter(status="PRESENT").count()
            absent = attendance.filter(status="ABSENT").count()
            leave = attendance.filter(status="LEAVE").count()

            percentage = 0
            if total > 0:
                percentage = round((present / total) * 100, 2)

            result.append({
                "subject": subject_name,
                "total": total,
                "present": present,
                "absent": absent,
                "leave": leave,
                "percentage": percentage
            })

        return Response(result)