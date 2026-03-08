from urllib import request

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from django.utils import timezone
from datetime import timedelta

from .models import HouseMaster, House
from .serializers import HouseMasterSerializer, HouseSerializer

from utils.permissions import IsPrincipal

from apps.students.models import Student
from apps.attendance.models import HouseAttendance 


# -----------------------------
# House CRUD (Principal only)
# -----------------------------
class HouseViewSet(ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [IsAuthenticated, IsPrincipal]


# -----------------------------
# House Master CRUD (Principal)
# -----------------------------
class HouseMasterViewSet(ModelViewSet):
    queryset = HouseMaster.objects.select_related("teacher", "house")
    serializer_class = HouseMasterSerializer
    permission_classes = [IsAuthenticated, IsPrincipal]


# -----------------------------
# House Master Dashboard
# -----------------------------
class HouseMasterDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        teacher = getattr(request.user, "teacher_profile", None)

        if not teacher:
            return Response({"detail": "Teacher profile not found"}, status=400)

        house_master = HouseMaster.objects.select_related("house").filter(
            teacher=teacher,
            is_house_master=True
        ).first()

        if not house_master:
            return Response({"detail": "Not a house master"}, status=403)

        house = house_master.house

        students = Student.objects.filter(house=house)

        total_students = students.count()

        today = timezone.now().date()

        attendance = HouseAttendance.objects.filter(
            house=house,
            date=today
        )

        present_today = attendance.filter(status="present").count()
        leave_today = attendance.filter(status="leave").count()

        attendance_percentage = 0
        if total_students > 0:
            attendance_percentage = round((present_today / total_students) * 100)

        return Response({
            "house": str(house),
            "totalStudents": total_students,
            "presentToday": present_today,
            "leaveToday": leave_today,
            "attendancePercentage": attendance_percentage
        })


# -----------------------------
# House Students List
# -----------------------------
class HouseStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        teacher = getattr(request.user, "teacher_profile", None)

        if not teacher:
            return Response({"detail": "Teacher profile not found"}, status=400)

        house_master = HouseMaster.objects.select_related("house").filter(
            teacher=teacher,
            is_house_master=True
        ).first()

        if not house_master:
            return Response({"detail": "Not a house master"}, status=403)

        house = house_master.house

        students = Student.objects.filter(
            house=house
        ).select_related("user", "classroom", "parent", "house")

        today = timezone.now().date()

        data = []

        for s in students:

            attendance = HouseAttendance.objects.filter(
                student=s,
                date=today
            ).first()

            status = attendance.status if attendance else None
            
            attendance_qs = HouseAttendance.objects.filter(student=s)
            
            total_days = attendance_qs.count()
            present_days = attendance_qs.filter(status="present").count()
            leave_days = attendance_qs.filter(status="leave").count()

            data.append({
                
                "id": s.id,
                
                # student info
                "name": f"{s.user.first_name} {s.user.last_name}",
                "gender": s.user.gender if s.user else "",
                "admission_number": s.admission_number,
                "class": s.classroom.class_name if s.classroom else "",
                "section": s.classroom.section if s.classroom else "",
                "photo": s.photo.url if s.photo else "",
                "house_name": s.house.house_name if s.house else "",
                "house_category": s.house.house_category if s.house else "",

                # parent info
                "parent": {
                    "Name": s.parent.get_full_name() if s.parent else "",
                    "Photo": s.parent.photo.url if s.parent and s.parent.photo else "",
                    "Phone1": s.parent.phone1 if s.parent else "",
                    "Phone2": s.parent.phone2 if s.parent else "",
                    "email": s.parent.email if s.parent else "",
                    "Occupation": s.parent.job if s.parent else "",
                    "Present_Address": s.parent.present_address if s.parent else "",
                    "Permanent_Address": s.parent.permanent_address if s.parent else "",
                },
                # attendance info
                "today_status": status,
                "attendance": {
                    "total": total_days,
                    "present": present_days,
                    "leave": leave_days,
                }
                
            })

        return Response(data)
    
class TakeHouseAttendanceView(APIView):

    permission_classes = [IsAuthenticated]
    
    def get(self, request):

        teacher = request.user.teacher_profile

        house_master = HouseMaster.objects.select_related("house").filter(
            teacher=teacher,
            is_house_master=True
        ).first()

        if not house_master:
            return Response({"detail": "Not a house master"}, status=403)

        house = house_master.house

        today = timezone.now().date()

        students = Student.objects.filter(
            house=house
        ).select_related("user", "classroom")

        data = []

        for s in students:

            attendance = HouseAttendance.objects.filter(
                student=s,
                date=today
            ).first()

            data.append({
                "student_id": s.id,
                "student_name": f"{s.user.first_name} {s.user.last_name}",
                "admission_number": s.admission_number,
                "class": s.classroom.class_name if s.classroom else "",
                "section": s.classroom.section if s.classroom else "",
                "status": attendance.status if attendance else None
            })

        return Response({
            "date": today,
            "students": data
        })

    def post(self, request):

        teacher = request.user.teacher_profile

        house_master = HouseMaster.objects.select_related("house").filter(
            teacher=teacher,
            is_house_master=True
        ).first()

        if not house_master:
            return Response({"detail": "Not a house master"}, status=403)

        house = house_master.house

        date = request.data.get("date")

        attendance_data = request.data.get("attendance_data", [])

        for item in attendance_data:

            student_id = item.get("student_id")
            status = item.get("status")

            student = Student.objects.get(id=student_id)

            # Update if exists, create if not
            HouseAttendance.objects.update_or_create(
                student=student,
                date=date,
                defaults={
                    "house": house,
                    "status": status,
                    "marked_by": request.user
                }
            )

        return Response({"message": "Attendance saved/updated successfully"})
    
    
class TodayLeaveStudentsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        teacher = request.user.teacher_profile

        house_master = HouseMaster.objects.select_related("house").filter(
            teacher=teacher,
            is_house_master=True
        ).first()

        if not house_master:
            return Response({"detail": "Not a house master"}, status=403)

        house = house_master.house
        today = timezone.now().date()

        attendance = HouseAttendance.objects.filter(
            house=house,
            date=today,
            status="leave"
        ).select_related("student__user")  
        # [:5]

        data = []

        for a in attendance:
            data.append({
                "name": f"{a.student.user.first_name} {a.student.user.last_name}",
                "status": a.status,
                "time": a.created_at.strftime("%H:%M")
            })

        return Response(data)