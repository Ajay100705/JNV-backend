from rest_framework import serializers
from .models import HouseAttendance
from apps.students.models import Student


class HouseAttendanceSerializer(serializers.ModelSerializer):

    student_name = serializers.CharField(source="student.user.get_full_name", read_only=True)
    admission_number = serializers.CharField(source="student.admission_number", read_only=True)

    class Meta:
        model = HouseAttendance
        fields = [
            "id",
            "student",
            "student_name",
            "admission_number",
            "house",
            "date",
            "status",
            "marked_by",
        ]
        read_only_fields = ["marked_by"]