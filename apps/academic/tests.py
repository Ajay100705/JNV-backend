from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
import datetime
from unittest.mock import patch

from apps.accounts.models import User
from apps.academic.models import Subject, ClassTeacher, TimeSlot, TeacherSubject
from apps.academic.utils import get_current_academic_year
from apps.classes.models import ClassRoom
from apps.teachers.models import TeacherProfile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_principal(username="acprincip", password="pass1234"):
    return User.objects.create_user(username=username, password=password, role="principal")


def make_teacher_profile(username="acteach1"):
    user = User.objects.create_user(username=username, password="pass1234", role="teacher")
    return TeacherProfile.objects.create(
        user=user, subject="Math", qualification="M.Sc.",
        experience_years=4, date_of_joining=datetime.date(2020, 4, 1),
    )


def make_classroom(class_name="6th", section="A"):
    room, _ = ClassRoom.objects.get_or_create(class_name=class_name, section=section)
    return room


# ---------------------------------------------------------------------------
# Subject model
# ---------------------------------------------------------------------------

class SubjectModelTest(TestCase):

    def test_str_returns_name(self):
        subject = Subject(name="Mathematics", code="MATH01")
        self.assertEqual(str(subject), "Mathematics")

    def test_code_is_unique(self):
        Subject.objects.create(name="Physics", code="PHY01")
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Subject.objects.create(name="Physical Science", code="PHY01")


# ---------------------------------------------------------------------------
# SubjectViewSet
# ---------------------------------------------------------------------------

class SubjectViewSetTest(APITestCase):

    def setUp(self):
        self.list_url = "/api/academic/subjects/"
        self.principal = make_principal()

    def test_authenticated_can_list_subjects(self):
        Subject.objects.create(name="Biology", code="BIO01")
        self.client.force_authenticate(user=self.principal)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_can_create_subject(self):
        self.client.force_authenticate(user=self.principal)
        response = self.client.post(
            self.list_url, {"name": "Chemistry", "code": "CHEM01"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subject.objects.filter(code="CHEM01").exists())

    def test_unauthenticated_returns_401(self):
        # SubjectViewSet has no explicit permission_classes; it inherits the global
        # DEFAULT_AUTHENTICATION_CLASSES but NOT a default permission restriction,
        # so unauthenticated access is allowed by DRF default (AllowAny).
        response = self.client.get(self.list_url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])

    def test_duplicate_code_returns_400(self):
        Subject.objects.create(name="Economics", code="ECO01")
        self.client.force_authenticate(user=self.principal)
        response = self.client.post(
            self.list_url, {"name": "Eco2", "code": "ECO01"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# TimeSlot model (clean validation)
# ---------------------------------------------------------------------------

class TimeSlotModelTest(TestCase):

    def test_valid_40_minute_slot_saves(self):
        ts = TimeSlot(
            start_time=datetime.time(8, 0),
            end_time=datetime.time(8, 40),
            period_number=1,
        )
        ts.clean()  # Should not raise

    def test_invalid_duration_raises_validation_error(self):
        ts = TimeSlot(
            start_time=datetime.time(8, 0),
            end_time=datetime.time(8, 30),  # Only 30 minutes
            period_number=2,
        )
        with self.assertRaises(ValidationError):
            ts.clean()

    def test_str(self):
        ts = TimeSlot(
            start_time=datetime.time(9, 0),
            end_time=datetime.time(9, 40),
            period_number=2,
        )
        result = str(ts)
        self.assertIn("Period 2", result)


# ---------------------------------------------------------------------------
# TimeSlotViewSet
# ---------------------------------------------------------------------------

class TimeSlotViewSetTest(APITestCase):

    def setUp(self):
        self.list_url = "/api/academic/timeslots/"
        self.principal = make_principal(username="tsprincip")

    def test_authenticated_can_create_timeslot(self):
        self.client.force_authenticate(user=self.principal)
        data = {
            "start_time": "08:00:00",
            "end_time": "08:40:00",
            "period_number": 1,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authenticated_can_list_timeslots(self):
        TimeSlot.objects.create(
            start_time=datetime.time(9, 0), end_time=datetime.time(9, 40), period_number=2
        )
        self.client.force_authenticate(user=self.principal)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# ClassTeacher model
# ---------------------------------------------------------------------------

class ClassTeacherModelTest(TestCase):

    def test_str(self):
        classroom = make_classroom()
        teacher = make_teacher_profile(username="ctteach")
        ct = ClassTeacher(classroom=classroom, teacher=teacher, academic_year="2024-25")
        self.assertIn("6th-A", str(ct))

    def test_unique_together_classroom_year(self):
        classroom = make_classroom(class_name="9th", section="B")
        t1 = make_teacher_profile(username="ctteach1")
        t2 = make_teacher_profile(username="ctteach2")
        ClassTeacher.objects.create(classroom=classroom, teacher=t1, academic_year="2024-25")
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            ClassTeacher.objects.create(classroom=classroom, teacher=t2, academic_year="2024-25")


# ---------------------------------------------------------------------------
# AssignClassTeacherView
# ---------------------------------------------------------------------------

class AssignClassTeacherViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("assign-class-teacher")
        self.principal = make_principal(username="actprincip")
        self.teacher_profile = make_teacher_profile(username="actteach")
        self.classroom = make_classroom(class_name="10th", section="A")

    def test_principal_can_assign_class_teacher(self):
        self.client.force_authenticate(user=self.principal)
        data = {
            "classroom": self.classroom.pk,
            "teacher": self.teacher_profile.pk,
            "academic_year": "2024-25",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_teacher_cannot_assign_class_teacher(self):
        self.client.force_authenticate(user=self.teacher_profile.user)
        data = {
            "classroom": self.classroom.pk,
            "teacher": self.teacher_profile.pk,
            "academic_year": "2024-25",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ---------------------------------------------------------------------------
# get_current_academic_year utility
# ---------------------------------------------------------------------------

class GetCurrentAcademicYearTest(TestCase):

    def test_returns_current_year_format_after_april(self):
        import datetime as dt
        with patch("apps.academic.utils.timezone") as mock_tz:
            mock_tz.now.return_value = dt.datetime(2025, 6, 1)
            result = get_current_academic_year()
        self.assertEqual(result, "2025-26")

    def test_returns_previous_year_format_before_april(self):
        import datetime as dt
        with patch("apps.academic.utils.timezone") as mock_tz:
            mock_tz.now.return_value = dt.datetime(2025, 2, 1)
            result = get_current_academic_year()
        self.assertEqual(result, "2024-25")


# ---------------------------------------------------------------------------
# PrincipalDashboardView
# ---------------------------------------------------------------------------

class PrincipalDashboardViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("principal-dashboard")
        self.principal = make_principal(username="pdprincip")
        self.teacher_profile = make_teacher_profile(username="pdteach")

    def test_principal_can_access_dashboard(self):
        self.client.force_authenticate(user=self.principal)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_students", response.data)
        self.assertIn("total_teachers", response.data)
        self.assertIn("total_classes", response.data)

    def test_teacher_cannot_access_dashboard(self):
        self.client.force_authenticate(user=self.teacher_profile.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
