from django.contrib import admin
from .models import Parent

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "phone1", "phone2", "job")
    search_fields = ( "first_name", "last_name", "email")

