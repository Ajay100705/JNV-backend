from rest_framework import serializers
from .models import ClassRoom
from .models import Exam, SubjectExam, StudentMark, SubjectExam, ClassSubject


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = "__all__"




class ExamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Exam
        fields = "__all__"


class SubjectExamSerializer(serializers.ModelSerializer):

    subject_name = serializers.CharField(source="subject.name", read_only=True)
    exam_name = serializers.CharField(source="exam.name", read_only=True)
    class_name = serializers.CharField(source="exam.class_name", read_only=True)

    class Meta:
        model = SubjectExam
        fields = [
            "id",
            "exam",
            "exam_name",
            "class_name",
            "subject",
            "subject_name",
            "total_marks"
        ]


class StudentMarkSerializer(serializers.ModelSerializer):

    student_name = serializers.CharField(source="student.name", read_only=True)
    subject_name = serializers.CharField(source="subject_exam.subject.name", read_only=True)

    class Meta:
        model = StudentMark
        fields = [
            "id",
            "student",
            "student_name",
            "subject_exam",
            "subject_name",
            "marks_obtained",
        ]
        
class ClassSubjectSerializer(serializers.ModelSerializer):

    subject_name = serializers.CharField(source="subject.name", read_only=True)
    class_name = serializers.SerializerMethodField()

    class Meta:
        model = ClassSubject
        fields = [
            "id",
            "classroom",
            "class_name",
            "subject",
            "subject_name",
            "is_exam_subject",
        ]

    def get_class_name(self, obj):
        return f"{obj.classroom.class_name}-{obj.classroom.section}"