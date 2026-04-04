from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
import datetime

from apps.accounts.models import User
from apps.teachers.models import TeacherProfile
from apps.houses.models import House, HouseMaster
from apps.students.models import Student
from apps.classes.models import ClassRoom
from apps.attendance.models import HouseAttendance


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_principal(username="atprincip", password="pass1234"):
    return User.objects.create_user(username=username, password=password, role="principal")


def make_teacher_with_profile(username="atteacher1", password="pass1234"):
    user = User.objects.create_user(username=username, password=password, role="teacher")
    profile = TeacherProfile.objects.create(
        user=user, subject="PE", qualification="B.Ed",
        experience_years=1, date_of_joining=datetime.date(2022, 4, 1),
    )
    return user, profile


def make_house(house_name="Araval", house_category="Junior"):
    h, _ = House.objects.get_or_create(house_name=house_name, house_category=house_category)
    return h


def make_student_in_house(house, username="atstudent1"):
    classroom, _ = ClassRoom.objects.get_or_create(class_name="6th", section="A")
    user = User.objects.create_user(username=username, password="pass", role="student")
    return Student.objects.create(user=user, classroom=classroom, house=house)


# ---------------------------------------------------------------------------
# HouseAttendance model
# ---------------------------------------------------------------------------

class HouseAttendanceModelTest(TestCase):

    def test_str(self):
        house = make_house(house_name="Shivalik", house_category="Senior")
        student_user = User.objects.create_user(username="hast1", password="p", role="student")
        student = Student.objects.create(user=student_user, house=house)
        att = HouseAttendance(
            student=student, house=house,
            date=timezone.now().date(), status="present"
        )
        result = str(att)
        self.assertIn("present", result)

    def test_unique_together_student_date(self):
        house = make_house(house_name="Udaygiri", house_category="Junior")
        student = make_student_in_house(house, username="dupstudent")
        today = timezone.now().date()
        HouseAttendance.objects.create(student=student, house=house, date=today, status="present")
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            HouseAttendance.objects.create(student=student, house=house, date=today, status="leave")


# ---------------------------------------------------------------------------
# MarkHouseAttendanceView
# ---------------------------------------------------------------------------

class MarkHouseAttendanceViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("mark-house-attendance")
        self.house = make_house(house_name="Nilgiri", house_category="Senior")
        self.teacher_user, self.teacher_profile = make_teacher_with_profile(username="markhmteach")
        HouseMaster.objects.create(
            teacher=self.teacher_profile, house=self.house, is_house_master=True
        )
        self.student = make_student_in_house(self.house, username="markstudent")
        self.principal = make_principal(username="markprincip")

    def test_house_master_can_mark_attendance(self):
        self.client.force_authenticate(user=self.teacher_user)
        data = {"student": self.student.pk, "status": "present"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            HouseAttendance.objects.filter(student=self.student, status="present").exists()
        )

    def test_non_house_master_returns_403(self):
        other_user, _ = make_teacher_with_profile(username="nothmmark")
        self.client.force_authenticate(user=other_user)
        data = {"student": self.student.pk, "status": "present"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_returns_401(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_marking_twice_updates_attendance(self):
        self.client.force_authenticate(user=self.teacher_user)
        data = {"student": self.student.pk, "status": "present"}
        self.client.post(self.url, data, format="json")
        data["status"] = "leave"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            HouseAttendance.objects.filter(student=self.student).last().status, "leave"
        )


# ---------------------------------------------------------------------------
# TodayHouseAttendanceView
# ---------------------------------------------------------------------------

class TodayHouseAttendanceViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("today-house-attendance")
        self.house = make_house(house_name="Araval", house_category="Senior")
        self.teacher_user, self.teacher_profile = make_teacher_with_profile(username="todayhmteach")
        HouseMaster.objects.create(
            teacher=self.teacher_profile, house=self.house, is_house_master=True
        )
        student = make_student_in_house(self.house, username="todaystudent")
        HouseAttendance.objects.create(
            student=student, house=self.house,
            date=timezone.now().date(), status="present"
        )

    def test_house_master_can_view_today_attendance(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_non_house_master_returns_403(self):
        other_user, _ = make_teacher_with_profile(username="nothmtoday")
        self.client.force_authenticate(user=other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
