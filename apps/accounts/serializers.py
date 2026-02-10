from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User




class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        user = authenticate(
            email=attrs.get('email'),
            password=attrs.get('password')
        )
        if not user:
            raise serializers.ValidationError('Invalid email or password')
        
        attrs['user'] = user
        return attrs
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'roll', 'first_name', 'last_name']
        read_only_fields = ['id', 'roll']



class ParentCreateSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']

        read_only_fields = ['id', 'roll']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.roll = 'parent'
        user.set_password(password)
        user.save()
        return user


class TeacherCreateSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']

        read_only_fields = ['id', 'roll']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.roll = 'teacher'
        user.set_password(password)
        user.save()
        return user

