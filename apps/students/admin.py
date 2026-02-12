from django.contrib import admin
from .models import Class, House, Student

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "section")
    search_fields = ("name", "section")

@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "house_master")
    search_fields = ("name", "house_master__user__email")

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "admission_number", "roll_number", "student_class", "house", "parent")
    search_fields = ("first_name", "last_name", "admission_number", "roll_number", "student_class__name", "house__name", "parent__user__email") 
    list_filter = ("student_class", "house", "gender", "is_active")
    ordering = ("admission_number",)



