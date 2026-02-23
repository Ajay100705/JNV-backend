from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'admission_number', 'classroom', 'house', 'parent')
    search_fields = ('user__username', 'admission_number')
    list_filter = ('classroom', 'house')
