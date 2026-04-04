from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from apps.accounts.models import User
from apps.classes.models import (
    ClassRoom, Exam, SubjectExam, StudentMark, ClassSubject,
    calculate_grade, ExamType,
)
from apps.academic.models import Subject
from apps.students.models import Student
from apps.houses.models import House


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_principal(username="cprincipal", password="pass1234"):
    return User.objects.create_user(username=username, password=password, role="principal")


def make_teacher(username="cteacher", password="pass1234"):
    return User.objects.create_user(username=username, password=password, role="teacher")


def make_classroom(class_name="6th", section="A"):
    room, _ = ClassRoom.objects.get_or_create(class_name=class_name, section=section)
    return room


# ---------------------------------------------------------------------------
# calculate_grade
# ---------------------------------------------------------------------------

class CalculateGradeTest(TestCase):

    def test_grade_a1_at_90(self):
        self.assertEqual(calculate_grade(90), "A1")

    def test_grade_a1_above_90(self):
        self.assertEqual(calculate_grade(95), "A1")

    def test_grade_a2_at_80(self):
        self.assertEqual(calculate_grade(80), "A2")

    def test_grade_b1_at_70(self):
        self.assertEqual(calculate_grade(70), "B1")

    def test_grade_b2_at_60(self):
        self.assertEqual(calculate_grade(60), "B2")

    def test_grade_c1_at_50(self):
        self.assertEqual(calculate_grade(50), "C1")

    def test_grade_c2_at_40(self):
        self.assertEqual(calculate_grade(40), "C2")

    def test_grade_f_below_40(self):
        self.assertEqual(calculate_grade(39), "F")

    def test_grade_f_at_zero(self):
        self.assertEqual(calculate_grade(0), "F")


# ---------------------------------------------------------------------------
# ClassRoom model
# ---------------------------------------------------------------------------

class ClassRoomModelTest(TestCase):

    def test_str(self):
        classroom = ClassRoom(class_name="7th", section="B")
        self.assertEqual(str(classroom), "7th-B")


# ---------------------------------------------------------------------------
# ClassRoom list view
# ---------------------------------------------------------------------------

class ClassRoomListViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("classroom-list")
        self.user = make_principal()
        ClassRoom.objects.create(class_name="6th", section="A")
        ClassRoom.objects.create(class_name="7th", section="B")

    def test_authenticated_returns_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ClassRoomDetailViewTest(APITestCase):

    def setUp(self):
        self.user = make_principal(username="detailprinc")
        self.classroom = ClassRoom.objects.create(class_name="8th", section="A")
        self.url = reverse("classroom-detail", kwargs={"pk": self.classroom.pk})

    def test_authenticated_returns_detail(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["class_name"], "8th")

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ---------------------------------------------------------------------------
# Exam model & views
# ---------------------------------------------------------------------------

class ExamModelTest(TestCase):

    def test_str(self):
        exam = Exam(name="UNIT1", class_name="6th")
        self.assertIn("6th", str(exam))

    def test_exam_type_choices(self):
        valid_types = [c[0] for c in ExamType.choices]
        self.assertIn("UNIT1", valid_types)
        self.assertIn("ENDTERM", valid_types)
        self.assertIn("MIDTERM", valid_types)


class ExamViewSetTest(APITestCase):

    def setUp(self):
        self.principal = make_principal(username="examprincip")
        self.teacher = make_teacher(username="examteach")
        self.list_url = "/api/classes/exams/"

    def test_authenticated_can_list_exams(self):
        self.client.force_authenticate(user=self.principal)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cannot_list_exams(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CreateExamViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("create-exam")
        self.principal = make_principal(username="createexamprincip")
        self.teacher = make_teacher(username="createexamteach")

    def test_principal_can_create_exam(self):
        self.client.force_authenticate(user=self.principal)
        data = {
            "class_name": "6th",
            "name": "UNIT1",
            "academic_year": "2024-25",
            "weightage": 10.0,
            "start_date": "2025-06-01",
            "end_date": "2025-06-10",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("exam", response.data)

    def test_teacher_cannot_create_exam(self):
        self.client.force_authenticate(user=self.teacher)
        data = {
            "class_name": "6th",
            "name": "UNIT1",
            "academic_year": "2024-25",
            "weightage": 10.0,
            "start_date": "2025-06-01",
            "end_date": "2025-06-10",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeleteExamViewTest(APITestCase):

    def setUp(self):
        self.principal = make_principal(username="delexamprincip")
        self.teacher = make_teacher(username="delexamteach")
        self.exam = Exam.objects.create(
            name="UNIT1",
            class_name="6th",
            academic_year="2024-25",
            weightage=10.0,
            start_date="2025-06-01",
            end_date="2025-06-10",
        )

    def test_principal_can_delete_exam(self):
        url = reverse("delete-exam", kwargs={"exam_id": self.exam.pk})
        self.client.force_authenticate(user=self.principal)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Exam.objects.filter(pk=self.exam.pk).exists())

    def test_teacher_cannot_delete_exam(self):
        url = reverse("delete-exam", kwargs={"exam_id": self.exam.pk})
        self.client.force_authenticate(user=self.teacher)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_nonexistent_exam_returns_404(self):
        url = reverse("delete-exam", kwargs={"exam_id": 99999})
        self.client.force_authenticate(user=self.principal)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DeleteExamTypeViewTest(APITestCase):

    def setUp(self):
        self.principal = make_principal(username="deltypeprincip")
        Exam.objects.create(
            name="UNIT2", class_name="6th", academic_year="2024-25",
            weightage=10.0, start_date="2025-06-01", end_date="2025-06-10",
        )
        Exam.objects.create(
            name="UNIT2", class_name="7th", academic_year="2024-25",
            weightage=10.0, start_date="2025-06-01", end_date="2025-06-10",
        )

    def test_principal_deletes_all_exams_of_type(self):
        url = reverse("delete-exam-type", kwargs={"name": "UNIT2"})
        self.client.force_authenticate(user=self.principal)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["deleted_count"], 2)
        self.assertEqual(Exam.objects.filter(name="UNIT2").count(), 0)


class BulkCreateExamsTest(APITestCase):

    def setUp(self):
        self.url = reverse("bulk-create-exams")
        self.principal = make_principal(username="bulkexamprincip")
        ClassRoom.objects.get_or_create(class_name="6th", section="A")
        ClassRoom.objects.get_or_create(class_name="7th", section="A")

    def test_principal_creates_exam_for_all_classes(self):
        self.client.force_authenticate(user=self.principal)
        data = {
            "name": "MIDTERM",
            "weightage": 20.0,
            "academic_year": "2024-25",
            "start_date": "2025-08-01",
            "end_date": "2025-08-10",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        classes = ClassRoom.objects.values_list("class_name", flat=True).distinct()
        for c in classes:
            self.assertTrue(
                Exam.objects.filter(name="MIDTERM", class_name=c, academic_year="2024-25").exists()
            )


# ---------------------------------------------------------------------------
# GenerateReportCard view
# ---------------------------------------------------------------------------

class GenerateReportCardTest(APITestCase):

    def setUp(self):
        self.principal = make_principal(username="reportprincip")
        classroom = make_classroom()
        student_user = User.objects.create_user(
            username="reportstudent", password="pass1234", role="student"
        )
        self.student = Student.objects.create(user=student_user, classroom=classroom)

    def test_empty_marks_returns_zero_percentage(self):
        url = reverse("report-card", kwargs={"student_id": self.student.pk})
        self.client.force_authenticate(user=self.principal)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["percentage"], 0.0)
        self.assertEqual(response.data["grade"], "F")

    def test_with_marks_calculates_grade(self):
        subject = Subject.objects.create(name="Math", code="MATH01")
        exam = Exam.objects.create(
            name="UNIT1", class_name="6th", academic_year="2024-25",
            weightage=100.0, start_date="2025-06-01", end_date="2025-06-10",
        )
        subj_exam = SubjectExam.objects.create(exam=exam, subject=subject, total_marks=100)
        StudentMark.objects.create(
            student=self.student, subject_exam=subj_exam, marks_obtained=85
        )
        url = reverse("report-card", kwargs={"student_id": self.student.pk})
        self.client.force_authenticate(user=self.principal)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertAlmostEqual(response.data["percentage"], 85.0, places=1)
        self.assertEqual(response.data["grade"], "A2")


# ---------------------------------------------------------------------------
# ClassSubject views
# ---------------------------------------------------------------------------

class ClassSubjectsByClassViewTest(APITestCase):
    """Tests ClassSubjectsByClassView by calling the view directly to avoid
    the router URL pattern shadowing the named URL."""

    def setUp(self):
        self.user = make_principal(username="csbyclass")
        self.classroom = make_classroom(class_name="9th", section="A")
        subject = Subject.objects.create(name="Science", code="SCI999")
        ClassSubject.objects.create(classroom=self.classroom, subject=subject)

    def test_returns_subjects_for_class(self):
        from rest_framework.test import APIRequestFactory, force_authenticate
        from apps.classes.views import ClassSubjectsByClassView
        factory = APIRequestFactory()
        request = factory.get("/")
        force_authenticate(request, user=self.user)
        view = ClassSubjectsByClassView.as_view()
        response = view(request, classroom_id=self.classroom.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subject_names = [item["subject_name"] for item in response.data]
        self.assertIn("Science", subject_names)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIRequestFactory
        from apps.classes.views import ClassSubjectsByClassView
        factory = APIRequestFactory()
        request = factory.get("/")
        view = ClassSubjectsByClassView.as_view()
        response = view(request, classroom_id=self.classroom.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
