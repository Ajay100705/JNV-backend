from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import HouseAttendance
from .serializers import HouseAttendanceSerializer

from apps.houses.models import HouseMaster
from apps.students.models import Student


class MarkHouseAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        student_id = request.data.get("student")
        status = request.data.get("status")

        teacher = request.user.teacher_profile

        house_master = HouseMaster.objects.select_related("house").filter(
            teacher=teacher,
            is_house_master=True
        ).first()

        if not house_master:
            return Response({"detail": "Not a house master"}, status=403)

        house = house_master.house

        student = Student.objects.get(id=student_id)

        today = timezone.now().date()

        attendance, created = HouseAttendance.objects.update_or_create(
            student=student,
            date=today,
            defaults={
                "house": house,
                "status": status,
                "marked_by": request.user
            }
        )

        serializer = HouseAttendanceSerializer(attendance)

        return Response(serializer.data)
    
class TodayHouseAttendanceView(APIView):
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
            date=today
        ).select_related("student__user")

        serializer = HouseAttendanceSerializer(attendance, many=True)

        return Response(serializer.data)