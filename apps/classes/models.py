from django.db import models
from utils.choices import CLASS, SECTION
# from apps.academic.models import Subject


class ClassRoom(models.Model):
    class_name = models.CharField(max_length=10, choices=CLASS)
    section = models.CharField(max_length=1, choices=SECTION)

    def __str__(self):
        return f"{self.class_name}-{self.section}"


class ExamType(models.TextChoices):
    UNIT1 = "UNIT1", "Unit Test 1"
    UNIT2 = "UNIT2", "Unit Test 2"
    MIDTERM = "MIDTERM", "Mid Term"
    UNIT3 = "UNIT3", "Unit Test 3"
    UNIT4 = "UNIT4", "Unit Test 4"
    ENDTERM = "ENDTERM", "End Term"  
    
class Exam(models.Model):

    name = models.CharField(max_length=20, choices=ExamType.choices)

    class_name = models.CharField(max_length=10)
        

    academic_year = models.CharField(max_length=9)

    weightage = models.FloatField(
        help_text="Percentage weightage (example: 10 for 10%)"
    )

    start_date = models.DateField()
    end_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_name_display()} - {self.class_name}"
class SubjectExam(models.Model):

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="subjects"
    )

    subject = models.ForeignKey(
        "academic.Subject",
        on_delete=models.CASCADE
    )

    total_marks = models.IntegerField(default=100)
    
    class Meta:
        unique_together = ("exam", "subject")

    def __str__(self):
        return f"{self.exam} - {self.subject}"

class StudentMark(models.Model):

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="marks"
    )

    subject_exam = models.ForeignKey(
        SubjectExam,
        on_delete=models.CASCADE,
        related_name="student_marks"
    )

    marks_obtained = models.FloatField()

    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "subject_exam")
        
    def __str__(self):
        return f"{self.student} - {self.subject_exam}"
    
class ReportCard(models.Model):

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE
    )

    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE
    )

    academic_year = models.CharField(max_length=9)

    total_marks = models.FloatField()
    percentage = models.FloatField()
    grade = models.CharField(max_length=5)

    created_at = models.DateTimeField(auto_now_add=True)
    
def calculate_grade(percentage):

    if percentage >= 90:
        return "A1"

    if percentage >= 80:
        return "A2"

    if percentage >= 70:
        return "B1"

    if percentage >= 60:
        return "B2"

    if percentage >= 50:
        return "C1"

    if percentage >= 40:
        return "C2"

    return "F"

class ClassSubject(models.Model):

    classroom = models.ForeignKey(
        "classes.ClassRoom",
        on_delete=models.CASCADE,
        related_name="subjects"
    )

    subject = models.ForeignKey(
        "academic.Subject",
        on_delete=models.CASCADE
    )

    is_exam_subject = models.BooleanField(default=True)

    class Meta:
        unique_together = ("classroom", "subject")

    def __str__(self):
        return f"{self.classroom} - {self.subject}"