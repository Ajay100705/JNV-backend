from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import TeacherProfile

User = get_user_model()

class TeacherProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    gender = serializers.CharField(source='user.gender', read_only=True)
    
    phone = serializers.CharField( read_only=True)
    

    class Meta:
        model = TeacherProfile
        fields = "__all__"

class TeacherProfileCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    gender = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
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
                  'phone',
                  'subject', 
                  'qualification', 
                  'experience_years', 
                  'date_of_joining', 
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
        phone = validated_data.pop('phone', None)
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

        teacher = TeacherProfile.objects.create(user=user, phone=phone, **validated_data)
        return teacher
    


    @transaction.atomic
    def update(self, instance, validated_data):
        user = instance.user

        username = validated_data.pop('username', None)
        phone = validated_data.pop('phone', None)

        if username:
            user.username = username

        user.save()

        if phone is not None:
            instance.phone = phone   # ✅ update phone

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance