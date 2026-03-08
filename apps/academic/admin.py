# apps/attendance/admin.py
from django.contrib import admin
from .models import Subject, ClassTeacher, TeacherSubject, TimeSlot, Timetable, Attendance

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']

@admin.register(ClassTeacher)
class ClassTeacherAdmin(admin.ModelAdmin):
    list_display = ['classroom', 'teacher', 'academic_year']
    list_filter = ['academic_year']
    search_fields = ['classroom__class_name', 'teacher__user__username']

@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'classroom']
    list_filter = ['subject']
    search_fields = ['teacher__user__username', 'subject__name']

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = [ 'period_number', 'start_time', 'end_time']
    ordering = ['period_number']

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['classroom', 'subject', 'teacher', 'time_slot', 'academic_year', 'is_active']
    list_filter = ['academic_year', 'is_active', 'classroom__class_name', 'day']
    search_fields = ['classroom__class_name', 'subject__name', 'teacher__user__username']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'timetable', 'date', 'status', 'marked_by']
    list_filter = ['status', 'date']
    search_fields = ['student__user__username', 'student__admission_number']
    date_hierarchy = 'date'