from rest_framework import serializers
from .models import House, HouseMaster
from apps.teachers.serializers import TeacherProfileSerializer
from apps.teachers.models import TeacherProfile


class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = "__all__"


class HouseMasterSerializer(serializers.ModelSerializer):

    # READ (nested)
    teacher_detail = TeacherProfileSerializer(source="teacher", read_only=True)
    house_detail = HouseSerializer(source="house", read_only=True)

    # WRITE (ids)
    teacher = serializers.PrimaryKeyRelatedField(queryset=TeacherProfile.objects.all())
    house = serializers.PrimaryKeyRelatedField(queryset=House.objects.all())

    class Meta:
        model = HouseMaster
        fields = [
            "id",
            "teacher",
            "house",
            "teacher_detail",
            "house_detail",
            "is_house_master",
        ]

    def validate(self, data):
        house = data["house"]

        if HouseMaster.objects.filter(house=house).count() >= 2:
            raise serializers.ValidationError("Each house can have at most 2 house masters.")

        return data