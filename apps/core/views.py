from apps.parents.models import Parent
from apps.students.models import Student
from apps.teachers.models import TeacherProfile
from apps.houses.models import HouseMaster, House
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count

class DashboardStatsViewSet(ViewSet):
    def list(self, request):
        total_students = Student.objects.count()
        total_teachers = TeacherProfile.objects.count()
        total_parents = Parent.objects.count()
        total_housemasters = HouseMaster.objects.count()

        stats = {
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_parents': total_parents,
            'total_housemasters': total_housemasters,
        }
        return Response(stats)
    
class HouseWiseStudentCountAPIView(APIView):
    def get(self, request):

        queryset = (
            Student.objects
            .filter(house__isnull=False)
            .values(
                "house__house_name",
                "house__house_category",
                )
            .annotate(student_count=Count("id"))
        )

        result = []

        for item in queryset:
            result.append({
                "house": item["house__house_name"],
                "category": item["house__house_category"],
                "student_count": item["student_count"]
            })

        return Response({"houseWiseStudents": result})