from rest_framework import serializers
from .models import Parent
from apps.students.models import Student

class StudentMiniSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class_name = serializers.CharField(source="classroom.class_name", read_only=True)
    section = serializers.CharField(source="classroom.section", read_only=True)

    house_name = serializers.CharField(source="house.house_name", read_only=True)
    house_category = serializers.CharField(source="house.house_category", read_only=True)

    photo = serializers.ImageField(read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "first_name",
            "last_name",
            "admission_number",
            "class_name",
            "section",
            "house_name",
            "house_category",
            "photo",
        ]
class ParentSerializer(serializers.ModelSerializer):
    children = StudentMiniSerializer(many=True, read_only=True)

    class Meta:
        model = Parent
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone1",
            "phone2",
            "job",
            "photo",
            "children",
        ]