from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Student
from apps.parents.models import Parent
from apps.classes.models import ClassRoom
from apps.houses.models import House

from apps.parents.serializers import ParentSerializer
from apps.classes.serializers import ClassroomSerializer
from apps.houses.serializers import HouseSerializer

User = get_user_model()


# ===========================
# LIST / DETAIL SERIALIZER
# ===========================

class StudentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    gender = serializers.CharField(source="user.gender", read_only=True)

    classroom = ClassroomSerializer()
    house = HouseSerializer()
    parent = ParentSerializer()

    class Meta:
        model = Student
        fields = "__all__"

    def get_classroom_name(self, obj):
        if obj.classroom:
            return f"{obj.classroom.class_name} {obj.classroom.section}"
        return None

    def get_parent_name(self, obj):
        if obj.parent:
            return f"{obj.parent.first_name} {obj.parent.last_name}"
        return None


# ===========================
# CREATE / UPDATE SERIALIZER
# ===========================

class StudentCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    gender = serializers.CharField(write_only=True)

    class_name = serializers.CharField(write_only=True)
    section = serializers.CharField(write_only=True)

    house_name = serializers.CharField(write_only=True)
    house_category = serializers.CharField(write_only=True)

    parent_first_name = serializers.CharField(write_only=True)
    parent_last_name = serializers.CharField(write_only=True)
    parent_phone1 = serializers.CharField(write_only=True)
    parent_phone2 = serializers.CharField(required=False, allow_blank=True, write_only=True)
    parent_email = serializers.EmailField(write_only=True)
    parent_job = serializers.CharField(required=False, allow_blank=True, write_only=True)
    present_address = serializers.CharField(write_only=True)
    permanent_address = serializers.CharField(write_only=True)
    parent_photo = serializers.ImageField(required=False, write_only=True)


    class Meta:
        model = Student
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "gender",

            "admission_date",
            "date_of_birth",
            "photo",

            "class_name",
            "section",

            "house_name",
            "house_category",

            "parent_first_name",
            "parent_last_name",
            "parent_phone1",
            "parent_phone2",
            "parent_email",
            "parent_job",
            "present_address",
            "permanent_address",
            "parent_photo"

        ]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    @transaction.atomic
    def create(self, validated_data):
    
        # Create user
        user = User.objects.create_user(
            first_name=validated_data.pop("first_name", ""),
            last_name=validated_data.pop("last_name", ""),
            email=validated_data.pop("email", ""),
            gender=validated_data.pop("gender", ""),
            username=validated_data.pop("username"), 
            password="student123",  # Set a default password or generate one
            role='student'
            )

        classroom, _ = ClassRoom.objects.get_or_create(
            class_name=validated_data.pop("class_name"),
            section=validated_data.pop("section")
        )

        house, _ = House.objects.get_or_create(
            house_name=validated_data.pop("house_name"),
            house_category=validated_data.pop("house_category")
        )  
        
        

        parent = Parent.objects.create(
            first_name=validated_data.pop("parent_first_name"),
            last_name=validated_data.pop("parent_last_name"),
            phone1=validated_data.pop("parent_phone1"),
            phone2=validated_data.pop("parent_phone2", ""),
            email=validated_data.pop("parent_email"),
            job=validated_data.pop("parent_job", ""),
            present_address=validated_data.pop("present_address"),
            permanent_address=validated_data.pop("permanent_address"),
            photo=validated_data.pop("parent_photo", None)
        )

        student = Student.objects.create(
            user=user,
            parent=parent,
            classroom=classroom,
            house=house,
            **validated_data
        )

        return student

    @transaction.atomic
    def update(self, instance, validated_data):
        user = instance.user

        if "username" in validated_data:
            user.username = validated_data.pop("username")

        if "password" in validated_data:
            user.set_password(validated_data.pop("password"))

        user.save()

        return super().update(instance, validated_data)