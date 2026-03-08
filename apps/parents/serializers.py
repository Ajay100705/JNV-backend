from rest_framework import serializers
from .models import Parent
from apps.students.models import Student
from django.contrib.auth import get_user_model

User = get_user_model()

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
    username = serializers.CharField(source="user.username", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)

    children = StudentMiniSerializer(many=True, read_only=True)

    class Meta:
        model = Parent
        fields = [
            "id",
            "username",
            "role",
            "first_name",
            "last_name",
            "email",
            "phone1",
            "phone2",
            "job",
            "present_address",
            "permanent_address",
            "photo",
            "children",
        ]
    def get_full_name(self, obj):
        return obj.get_full_name()
    
class ParentUpdateSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username")
    class Meta:
        model = Parent
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone1",
            "phone2",
            "job",
            "present_address",
            "permanent_address",
            "photo",
        ]
        
    def validate(self, attrs):

        user_data = attrs.get("user", {})
        username = user_data.get("username")
        email = attrs.get("email")

        parent = self.instance

        # check duplicate username
        if username:
            if User.objects.filter(username=username).exclude(id=parent.user.id).exists():
                raise serializers.ValidationError(
                    {"username": "This username is already taken"}
                )

        # check duplicate email
        if email:
            if Parent.objects.filter(email=email).exclude(id=parent.id).exists():
                raise serializers.ValidationError(
                    {"email": "This email is already used"}
                )

        return attrs

    def update(self, instance, validated_data):

        user_data = validated_data.pop("user", None)

        if user_data and "username" in user_data:
            instance.user.username = user_data["username"]
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance