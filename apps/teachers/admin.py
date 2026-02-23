from django.contrib import admin
from .models import TeacherProfile

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'qualification', 'experience_years', 'date_of_joining')
    search_fields = ('user__username', 'subject', 'qualification')
    list_filter = ('subject', 'qualification', 'experience_years')
    

