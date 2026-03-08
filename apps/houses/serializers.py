from rest_framework import serializers
from .models import House, HouseMaster
from apps.teachers.serializers import TeacherProfileSerializer
from apps.teachers.models import TeacherProfile


class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = "__all__"


class HouseMasterSerializer(serializers.ModelSerializer):

    # READ
    teacher_detail = TeacherProfileSerializer(source="teacher", read_only=True)
    house_detail = HouseSerializer(source="house", read_only=True)

    # WRITE
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
        teacher = data["teacher"]

        # Prevent more than 2 teachers per house
        if HouseMaster.objects.filter(house=house).count() >= 2:
            raise serializers.ValidationError(
                "Each house can have at most 2 teachers."
            )

        # Prevent same teacher twice in same house
        if HouseMaster.objects.filter(house=house, teacher=teacher).exists():
            raise serializers.ValidationError(
                "This teacher is already assigned to this house."
            )

        return data

    def create(self, validated_data):
        house = validated_data["house"]

        existing = HouseMaster.objects.filter(house=house).count()

        # First teacher → House Master
        if existing == 0:
            validated_data["is_house_master"] = True

        # Second teacher → Assistant
        elif existing == 1:
            validated_data["is_house_master"] = True

        return super().create(validated_data)