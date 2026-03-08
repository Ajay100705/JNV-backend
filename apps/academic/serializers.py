from django.forms import ValidationError
from rest_framework import serializers
from django.utils import timezone
from .models import Subject, TimeSlot, Timetable, Attendance, ClassTeacher, TeacherSubject
from apps.students.models import Student
from apps.classes.models import ClassRoom
from apps.teachers.models import TeacherProfile



class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code']

class ClassTeacherSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source='classroom.__str__', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    teacher_photo = serializers.ImageField(source='teacher.photo', read_only=True)
    teacher_phone = serializers.CharField(source='teacher.phone1', read_only=True)
    
    class Meta:
        model = ClassTeacher
        fields = ['id', 'classroom', 'classroom_name', 'teacher', 'teacher_name','teacher_photo' ,'teacher_phone', 'academic_year']

class TeacherSubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.__str__', read_only=True)
    
    class Meta:
        model = TeacherSubject
        fields = ['id', 'teacher', 'teacher_name', 'subject', 'subject_name', 
                 'classroom', 'classroom_name']
        
class TimeSlotSerializer(serializers.ModelSerializer):
    day_display = serializers.CharField(source='get_day_display', read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = ['id', 'day_display', 'start_time', 'end_time', 'period_number']

class TimetableSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source='classroom.__str__', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    time_slot_detail = TimeSlotSerializer(source='time_slot', read_only=True)
    
    class Meta:
        model = Timetable
        fields = ['id', 'classroom', 'day', 'classroom_name', 'subject', 'subject_name',
                 'teacher', 'teacher_name', 'time_slot', 'time_slot_detail',
                 'academic_year', 'is_active']
        
    def clean(self):

        # Teacher conflict
        if Timetable.objects.filter(
            teacher=self.teacher,
            time_slot=self.time_slot,
            day=self.day,
            academic_year=self.academic_year
        ).exclude(id=self.id).exists():

            raise ValidationError(
                "Teacher already assigned to another class in this period."
            )

        # Class conflict
        if Timetable.objects.filter(
            classroom=self.classroom,
            time_slot=self.time_slot,
            day=self.day,
            academic_year=self.academic_year
        ).exclude(id=self.id).exists():

            raise ValidationError(
                "This class already has a subject scheduled for this period."
            )

        # Subject teacher validation
        if not TeacherSubject.objects.filter(
            teacher=self.teacher,
            subject=self.subject,
            classroom=self.classroom
        ).exists():

            raise ValidationError(
                "Teacher is not assigned to this subject in this class."
            )
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.__str__', read_only=True)
    student_admission = serializers.CharField(source='student.admission_number', read_only=True)
    subject_name = serializers.CharField(source='timetable.subject.name', read_only=True)
    classroom_name = serializers.CharField(source='timetable.classroom.__str__', read_only=True)
    period_number = serializers.IntegerField(source='timetable.time_slot.period_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_name', 'student_admission', 'timetable',
                 'subject_name', 'classroom_name', 'period_number', 'date',
                 'status', 'status_display', 'marked_by', 'marked_at', 'remarks']
        
class BulkAttendanceSerializer(serializers.Serializer):
    date = serializers.DateField()
    timetable_id = serializers.IntegerField()
    attendance_data = serializers.ListField(
        child=serializers.DictField()
    )

    def validate(self, data):
        # Validate that all students belong to the same class
        timetable = Timetable.objects.get(id=data['timetable_id'])
        classroom = timetable.classroom
        
        for att in data['attendance_data']:
            if 'student_id' not in att or 'status' not in att:
                raise serializers.ValidationError("Each attendance must have student_id and status")
            
            try:
                student = Student.objects.get(id=att['student_id'])
                if student.classroom != classroom:
                    raise serializers.ValidationError(f"Student {student} does not belong to class {classroom}")
            except Student.DoesNotExist:
                raise serializers.ValidationError(f"Student with id {att['student_id']} does not exist")
        
        return data
    
class TodayClassSerializer(serializers.Serializer):
    period_number = serializers.IntegerField()
    subject = serializers.CharField(source='timetable.subject.name')
    teacher = serializers.CharField(source='timetable.teacher.__str__')
    classroom = serializers.CharField(source='timetable.classroom.__str__')
    time_slot = serializers.CharField(source='timetable.time_slot.__str__')
    attendance_status = serializers.CharField(allow_null=True)
