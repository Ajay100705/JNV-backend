from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import TeacherProfile
from apps.academic.models import ClassTeacher
from django.utils import timezone
from apps.houses.models import HouseMaster

User = get_user_model()

class TeacherProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    gender = serializers.CharField(source='user.gender', read_only=True)

    is_class_teacher = serializers.SerializerMethodField()
    class_teacher_of = serializers.SerializerMethodField()
    
    is_house_master = serializers.SerializerMethodField()
    house_name = serializers.SerializerMethodField()
    
    phone1 = serializers.CharField( read_only=True)
    phone2 = serializers.CharField( read_only=True)
    

    class Meta:
        model = TeacherProfile
        fields = [
            "id",
            "user",
            "first_name",
            "last_name",
            "username",
            "email",
            "gender",
            "subject",
            "qualification",
            "experience_years",
            "date_of_joining",
            "present_address",
            "permanent_address",
            "phone1",
            "phone2",
            "photo",
            "is_class_teacher",
            "class_teacher_of",
            "is_house_master",
            "house_name",
        ]

    def get_is_class_teacher(self, obj):
        current_year = self.get_current_academic_year()
        return ClassTeacher.objects.filter(
            teacher=obj,
            academic_year=current_year
        ).exists()

    def get_class_teacher_of(self, obj):
        current_year = self.get_current_academic_year()
        class_teacher = ClassTeacher.objects.filter(
            teacher=obj,
            academic_year=current_year
        ).select_related("classroom").first()

        if class_teacher:
            return str(class_teacher.classroom)
        return None
    
    def get_is_house_master(self, obj):
        # current_year = self.get_current_academic_year()

        return HouseMaster.objects.filter(
            teacher=obj,
            # academic_year=current_year,
            is_house_master=True
        ).exists()

    def get_house_name(self, obj):
        # current_year = self.get_current_academic_year()

        house_master = HouseMaster.objects.filter(
            teacher=obj,
            # academic_year=current_year
        ).select_related("house").first()

        if house_master:
            return str(house_master.house)

        return None

    def get_current_academic_year(self):
        now = timezone.now()
        year = now.year
        month = now.month

        if month < 4:
            return f"{year - 1}-{str(year)[-2:]}"
        return f"{year}-{str(year + 1)[-2:]}"



class TeacherProfileCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    gender = serializers.CharField(write_only=True)
    phone1 = serializers.CharField(write_only=True, required=False, allow_blank=True)
    phone2 = serializers.CharField(write_only=True, required=False, allow_blank=True)
    username = serializers.CharField(write_only=True)
    # password = serializers.CharField(write_only=True)

    class Meta:
        model = TeacherProfile
        fields = ['username',
                #   'password', 
                  'first_name',
                  'last_name',
                  'email',
                  'gender',
                  'phone1',
                  'phone2',
                  'subject', 
                  'qualification', 
                  'experience_years', 
                  'date_of_joining',
                    'present_address',
                    'permanent_address', 
                  'photo'
                  ]
    def validate_username(self, value):
        qs = User.objects.filter(username=value)

        if self.instance:
            qs = qs.exclude(pk=self.instance.user.pk)

        if qs.exists():
            raise serializers.ValidationError("Username already exists.")

        return value
    
    @transaction.atomic
    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')
        gender = validated_data.pop('gender')
        phone1 = validated_data.pop('phone1', None)
        phone2 = validated_data.pop('phone2', None)
        username = validated_data.pop('username')
        
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            gender=gender,
            username=username, 
            password="teacher123",  # Set a default password or generate one
            role='teacher'
            )

        teacher = TeacherProfile.objects.create(user=user, phone1=phone1, phone2=phone2, **validated_data)
        return teacher
    


    @transaction.atomic
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
        user = self.instance.user if self.instance else None

        qs = User.objects.filter(email=value)

        if user:
            qs = qs.exclude(pk=user.pk)

        if qs.exists():
            raise serializers.ValidationError("Email already in use.")

        return value
    



    

    

