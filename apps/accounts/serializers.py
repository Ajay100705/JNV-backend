from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User , PrincipalProfile
from django.contrib.auth import authenticate
from apps.teachers.serializers import TeacherProfileSerializer
from apps.students.serializers import StudentSerializer
from apps.parents.serializers import ParentSerializer

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "gender",
            "profile",
        ]

    def get_profile(self, obj):
        try:
            if obj.role == "principal" :
                return PrincipalProfileSerializer(obj.principal_profile).data

            if obj.role == "teacher" :
                return TeacherProfileSerializer(obj.teacher_profile).data

            if obj.role == "student" :
                return StudentSerializer(obj.student_profile).data
            if obj.role == "parent" :
                return ParentSerializer(obj.parent_profile).data

        except Exception as e:
            return None
        return None

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")
        
        refresh = RefreshToken.for_user(user)
        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
            },
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class PrincipalProfileSerializer(serializers.ModelSerializer):

    # User fields mapped correctly
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    username = serializers.CharField(source="user.username", required=False)
    email = serializers.EmailField(source="user.email", required=False)
    gender = serializers.CharField(source="user.gender", required=False)

    class Meta:
        model = PrincipalProfile
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "gender",

            "phone1",
            "phone2",
            "photo",
            "present_address",
            "permanent_address",
            "bio",
            "joining_date"
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        user = instance.user

        # Update User fields
        user.first_name = user_data.get("first_name", user.first_name)
        user.last_name = user_data.get("last_name", user.last_name)
        user.username = user_data.get("username", user.username)
        user.email = user_data.get("email", user.email)
        user.gender = user_data.get("gender", user.gender)
        user.save()

        # Update PrincipalProfile fields
        return super().update(instance, validated_data)

    def validate_email(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Email already in use.")
        return value

    
