from django.db import models
from django.forms import ValidationError
from utils.choices import DAYS, ATTENDANCE_STATUS
from apps.classes.models import ClassRoom
from apps.teachers.models import TeacherProfile
from apps.students.models import Student
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()




class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name
    
class ClassTeacher(models.Model):
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='class_teacher')
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='class_teacher_of')
    academic_year = models.CharField(max_length=9)

    class Meta:
        unique_together = [
            ('classroom', 'academic_year'),
            ('teacher', 'academic_year'),
        ]


    def __str__(self):
        return f"{self.classroom} - {self.teacher}"
    
class TeacherSubject(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('teacher', 'subject', 'classroom')
    
    def __str__(self):
        return f"{self.teacher} - {self.subject} - {self.classroom}"
    
class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    period_number = models.IntegerField()
    
    class Meta:
        ordering = [ 'period_number']
        
    
    def __str__(self):
        return f"Period {self.period_number} ({self.start_time} - {self.end_time})"
    
    def clean(self):
        # Validate time slots are 40 minutes with 5 minutes break
        if self.start_time and self.end_time:
            start = self.start_time
            end = self.end_time
            duration = (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)
            if duration != 40:
                raise ValidationError("Each class must be exactly 40 minutes")
    
class Timetable(models.Model):
    day = models.CharField(max_length=10, choices=DAYS)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='timetables')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE )
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=9)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('classroom', 'time_slot','day', 'academic_year')

    def clean(self):
        if not TeacherSubject.objects.filter(
            teacher=self.teacher,
            subject=self.subject,
            classroom=self.classroom
        ).exists():
            raise ValidationError("Teacher not assigned to this subject in this class")
        
    def __str__(self):
        return f"{self.classroom} - {self.subject} - {self.time_slot}"

class Attendance(models.Model):
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS)
    marked_by = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, related_name='marked_attendances')
    marked_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('student', 'timetable', 'date')
    
    def __str__(self):
        return f"{self.student} - {self.timetable} - {self.date} - {self.status}"

class TeacherUnavailable(models.Model):

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={"role": "teacher"})
    day = models.CharField(max_length=10)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.teacher} unavailable {self.day}"