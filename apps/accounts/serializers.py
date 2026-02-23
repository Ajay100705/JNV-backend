from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'gender']


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


# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
#     # password2 = serializers.CharField(write_only=True, required=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'first_name', 'last_name', 'role', 'gender', 'password']

#     # def validate(self, attrs):
#     #     if attrs['password'] != attrs['password2']:
#     #         raise serializers.ValidationError({"password": "Password fields didn't match."})
#     #     return attrs

#     def create(self, validated_data):
#         user = User.objects.create(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             first_name=validated_data['first_name'],
#             last_name=validated_data['last_name'],
#             role=validated_data['role'],
#             gender=validated_data['gender']
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#         return user