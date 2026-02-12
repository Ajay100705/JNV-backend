from django.contrib import admin
from .models import User, ParentProfile, TeacherProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id','email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'role')

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone')
    # search_fields = ('user__email', 'phone')

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone')
    # search_fields = ('user__email', 'phone')


