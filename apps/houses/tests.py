from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
import datetime

from apps.accounts.models import User
from apps.teachers.models import TeacherProfile
from apps.houses.models import House, HouseMaster


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_principal(username="hprincip", password="pass1234"):
    return User.objects.create_user(username=username, password=password, role="principal")


def make_teacher_user(username="hteacher1", password="pass1234"):
    return User.objects.create_user(username=username, password=password, role="teacher")


def make_teacher_profile(username="htprofile1"):
    user = make_teacher_user(username=username)
    return TeacherProfile.objects.create(
        user=user,
        subject="English",
        qualification="B.Ed",
        experience_years=2,
        date_of_joining=datetime.date(2021, 4, 1),
    )


def make_house(house_name="Araval", house_category="Junior"):
    h, _ = House.objects.get_or_create(house_name=house_name, house_category=house_category)
    return h


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class HouseModelTest(TestCase):

    def test_str(self):
        house = House(house_name="Nilgiri", house_category="Senior")
        self.assertIn("Nilgiri", str(house))
        self.assertIn("Senior", str(house))


class HouseMasterModelTest(TestCase):

    def setUp(self):
        self.house = make_house(house_name="Shivalik", house_category="Junior")
        self.t1 = make_teacher_profile(username="hmteach1")
        self.t2 = make_teacher_profile(username="hmteach2")
        self.t3 = make_teacher_profile(username="hmteach3")

    def test_first_teacher_becomes_house_master(self):
        hm = HouseMaster.objects.create(
            teacher=self.t1, house=self.house, is_house_master=True
        )
        self.assertTrue(hm.is_house_master)

    def test_more_than_two_teachers_raises_validation_error(self):
        HouseMaster.objects.create(teacher=self.t1, house=self.house, is_house_master=True)
        HouseMaster.objects.create(teacher=self.t2, house=self.house, is_house_master=True)
        with self.assertRaises(ValidationError):
            HouseMaster.objects.create(teacher=self.t3, house=self.house, is_house_master=False)


# ---------------------------------------------------------------------------
# HouseViewSet (principal only)
# ---------------------------------------------------------------------------

class HouseViewSetTest(APITestCase):

    def setUp(self):
        self.list_url = "/api/houses/houses/"
        self.principal = make_principal()
        self.house = make_house()

    def test_principal_can_list_houses(self):
        self.client.force_authenticate(user=self.principal)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_principal_returns_403(self):
        teacher_profile = make_teacher_profile(username="hvsteach")
        self.client.force_authenticate(user=teacher_profile.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_principal_can_create_house(self):
        self.client.force_authenticate(user=self.principal)
        data = {"house_name": "Udaygiri", "house_category": "Senior"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_principal_can_delete_house(self):
        h = House.objects.create(house_name="Nilgiri", house_category="Senior")
        self.client.force_authenticate(user=self.principal)
        url = f"/api/houses/houses/{h.pk}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# HouseMasterViewSet (principal only)
# ---------------------------------------------------------------------------

class HouseMasterViewSetTest(APITestCase):

    def setUp(self):
        self.list_url = "/api/houses/house-masters/"
        self.principal = make_principal(username="hmvprincip")
        self.house = make_house(house_name="Araval", house_category="Junior")
        self.teacher_profile = make_teacher_profile(username="hmvteach")
        HouseMaster.objects.create(
            teacher=self.teacher_profile, house=self.house, is_house_master=True
        )

    def test_principal_can_list_house_masters(self):
        self.client.force_authenticate(user=self.principal)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_non_principal_returns_403(self):
        self.client.force_authenticate(user=self.teacher_profile.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ---------------------------------------------------------------------------
# HouseMasterDashboardView
# ---------------------------------------------------------------------------

class HouseMasterDashboardViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("house-master-dashboard")
        self.principal = make_principal(username="hmdprincip")
        self.teacher_profile = make_teacher_profile(username="hmdteach")
        self.house = make_house(house_name="Nilgiri", house_category="Junior")
        HouseMaster.objects.create(
            teacher=self.teacher_profile, house=self.house, is_house_master=True
        )

    def test_house_master_can_access_dashboard(self):
        self.client.force_authenticate(user=self.teacher_profile.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("totalStudents", response.data)
        self.assertIn("presentToday", response.data)

    def test_non_house_master_teacher_gets_403(self):
        other_teacher = make_teacher_profile(username="nothmteach")
        self.client.force_authenticate(user=other_teacher.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_without_teacher_profile_gets_400(self):
        self.client.force_authenticate(user=self.principal)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
