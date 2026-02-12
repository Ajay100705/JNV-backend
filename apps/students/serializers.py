from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(
        source="parent.user.email",
        read_only=True
    )
    class_name = serializers.SerializerMethodField()
    house_name = serializers.CharField(
        source="house.name",
        read_only=True
    )

    class Meta:
        model = Student
        fields = [
            "id",
            "admission_number",
            "roll_number",
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",

            # WRITE FIELD
            "parent",

            # READ FIELDS
            "parent_name",
            "student_class",
            "class_name",
            "house",
            "house_name",

            "is_active",
        ]
        read_only_fields = ["id"]

    def get_class_name(self, obj):
        if obj.student_class:
            return str(obj.student_class)
        return None
