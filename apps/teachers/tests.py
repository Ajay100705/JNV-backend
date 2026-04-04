from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
import datetime

from apps.accounts.models import User
from apps.teachers.models import TeacherProfile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_principal(username="tprincip", password="pass1234"):
    return User.objects.create_user(username=username, password=password, role="principal")


def make_teacher_user(username="tuser1", password="pass1234"):
    return User.objects.create_user(username=username, password=password, role="teacher")


def make_teacher_profile(username="tprofile1", password="pass1234"):
    user = make_teacher_user(username=username, password=password)
    return TeacherProfile.objects.create(
        user=user,
        subject="Mathematics",
        qualification="B.Ed",
        experience_years=3,
        date_of_joining=datetime.date(2020, 4, 1),
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TeacherProfileModelTest(TestCase):

    def test_str(self):
        user = make_teacher_user(username="strteacher")
        profile = TeacherProfile(user=user, subject="Physics")
        result = str(profile)
        self.assertIn("strteacher", result)
        self.assertIn("Teacher", result)
        self.assertIn("Physics", result)

    def test_get_full_name(self):
        user = make_teacher_user(username="fullnameteacher")
        user.first_name = "Alice"
        user.last_name = "Jones"
        user.save()
        profile = TeacherProfile(user=user, subject="Chemistry")
        self.assertEqual(profile.get_full_name(), "Alice Jones")


# ---------------------------------------------------------------------------
# TeacherProfileViewSet (principal-only CRUD)
# ---------------------------------------------------------------------------

class TeacherProfileViewSetTest(APITestCase):

    def setUp(self):
        self.list_url = "/api/teachers/"
        self.principal = make_principal()
        self.teacher_profile = make_teacher_profile()

    def test_principal_can_list_teachers(self):
        self.client.force_authenticate(user=self.principal)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_unauthenticated_cannot_list_teachers(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_principal_cannot_list_teachers(self):
        self.client.force_authenticate(user=self.teacher_profile.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_principal_can_create_teacher(self):
        self.client.force_authenticate(user=self.principal)
        data = {
            "username": "newteacher001",
            "first_name": "Bob",
            "last_name": "Smith",
            "email": "bob@school.com",
            "gender": "male",
            "subject": "History",
            "qualification": "M.A.",
            "experience_years": 5,
            "date_of_joining": "2019-04-01",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TeacherProfile.objects.filter(user__username="newteacher001").exists())

    def test_principal_can_retrieve_teacher(self):
        self.client.force_authenticate(user=self.principal)
        url = f"/api/teachers/{self.teacher_profile.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_principal_can_delete_teacher(self):
        profile = make_teacher_profile(username="todelete")
        self.client.force_authenticate(user=self.principal)
        url = f"/api/teachers/{profile.pk}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# UpdateTeacherProfileView
# ---------------------------------------------------------------------------

class UpdateTeacherProfileViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("update-teacher-profile")
        self.principal = make_principal(username="upteachprincip")
        self.teacher_profile = make_teacher_profile(username="updateteach")

    def test_teacher_can_update_own_profile(self):
        self.client.force_authenticate(user=self.teacher_profile.user)
        response = self.client.put(
            self.url, {"subject": "Biology"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_teacher_non_principal_gets_403(self):
        student_user = User.objects.create_user(
            username="stuupdateteach", password="pass", role="student"
        )
        self.client.force_authenticate(user=student_user)
        response = self.client.put(
            self.url, {"subject": "Art"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_returns_401(self):
        response = self.client.put(self.url, {"subject": "Art"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
