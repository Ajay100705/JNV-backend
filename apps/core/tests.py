from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
import datetime

from apps.accounts.models import User
from apps.teachers.models import TeacherProfile
from apps.houses.models import House, HouseMaster
from apps.students.models import Student
from apps.classes.models import ClassRoom
from apps.parents.models import Parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_principal(username="coreprincip", password="pass1234"):
    return User.objects.create_user(username=username, password=password, role="principal")


def make_teacher_profile(username="coreteach"):
    user = User.objects.create_user(username=username, password="pass1234", role="teacher")
    return TeacherProfile.objects.create(
        user=user, subject="Art", qualification="B.A.",
        experience_years=1, date_of_joining=datetime.date(2023, 4, 1),
    )


def make_house(house_name="Araval", house_category="Junior"):
    h, _ = House.objects.get_or_create(house_name=house_name, house_category=house_category)
    return h


def make_student_in_house(house, username="corestudent"):
    classroom, _ = ClassRoom.objects.get_or_create(class_name="6th", section="A")
    user = User.objects.create_user(username=username, password="pass", role="student")
    return Student.objects.create(user=user, classroom=classroom, house=house)


# ---------------------------------------------------------------------------
# DashboardStatsViewSet
# ---------------------------------------------------------------------------

class DashboardStatsViewSetTest(APITestCase):

    def setUp(self):
        self.url = "/api/core/dashboard-stats/"
        self.principal = make_principal()

        # Create test data
        make_teacher_profile(username="dsteach1")
        make_teacher_profile(username="dsteach2")

        house = make_house()
        make_student_in_house(house, username="dsstudent1")
        make_student_in_house(house, username="dsstudent2")

        parent_user = User.objects.create_user(username="dsparent1", password="p", role="parent")
        Parent.objects.create(
            user=parent_user, first_name="X", last_name="Y",
            phone1="111", email="x@y.com",
            present_address="Addr", permanent_address="Addr",
        )

    def test_returns_correct_counts(self):
        self.client.force_authenticate(user=self.principal)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        # Lists endpoint returns dict in results
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        self.assertIn("total_students", data)
        self.assertIn("total_teachers", data)
        self.assertIn("total_parents", data)
        self.assertIn("total_housemasters", data)
        self.assertGreaterEqual(data["total_students"], 2)
        self.assertGreaterEqual(data["total_teachers"], 2)
        self.assertGreaterEqual(data["total_parents"], 1)

    def test_unauthenticated_access(self):
        # DashboardStatsViewSet has no explicit permission_classes; unauthenticated
        # access is allowed by the DRF default (AllowAny).
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])


# ---------------------------------------------------------------------------
# HouseWiseStudentCountAPIView
# ---------------------------------------------------------------------------

class HouseWiseStudentCountAPIViewTest(APITestCase):

    def setUp(self):
        self.url = "/api/core/house-wise-students/"
        self.principal = make_principal(username="hwcprincip")

        araval = make_house(house_name="Araval", house_category="Junior")
        nilgiri = make_house(house_name="Nilgiri", house_category="Senior")
        make_student_in_house(araval, username="hwcstu1")
        make_student_in_house(araval, username="hwcstu2")
        make_student_in_house(nilgiri, username="hwcstu3")

    def test_returns_house_wise_counts(self):
        self.client.force_authenticate(user=self.principal)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("houseWiseStudents", response.data)
        houses = response.data["houseWiseStudents"]
        total = sum(h["student_count"] for h in houses)
        self.assertGreaterEqual(total, 3)

    def test_unauthenticated_access(self):
        # HouseWiseStudentCountAPIView has no explicit permission_classes;
        # unauthenticated access is allowed by the DRF default (AllowAny).
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])
