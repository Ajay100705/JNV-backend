from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone

from apps.accounts.models import User
from apps.classes.models import ClassRoom
from apps.houses.models import House
from apps.students.models import Student


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_principal(username="sprincip", password="pass1234"):
    return User.objects.create_user(username=username, password=password, role="principal")


def make_student_user(username="stu1", password="pass1234"):
    return User.objects.create_user(username=username, password=password, role="student")


def make_classroom(class_name="6th", section="A"):
    room, _ = ClassRoom.objects.get_or_create(class_name=class_name, section=section)
    return room


def make_house(house_name="Araval", house_category="Junior"):
    h, _ = House.objects.get_or_create(house_name=house_name, house_category=house_category)
    return h


# ---------------------------------------------------------------------------
# Student model
# ---------------------------------------------------------------------------

class StudentModelTest(TestCase):

    def setUp(self):
        self.classroom = make_classroom()

    def test_admission_number_auto_generated(self):
        user = make_student_user(username="autostu1")
        student = Student.objects.create(user=user, classroom=self.classroom)
        year = timezone.now().year
        self.assertTrue(student.admission_number.startswith(f"JNV-{year}-"))

    def test_sequential_admission_numbers(self):
        u1 = make_student_user(username="seqstu1")
        u2 = make_student_user(username="seqstu2")
        s1 = Student.objects.create(user=u1, classroom=self.classroom)
        s2 = Student.objects.create(user=u2, classroom=self.classroom)
        n1 = int(s1.admission_number.split("-")[-1])
        n2 = int(s2.admission_number.split("-")[-1])
        self.assertEqual(n2, n1 + 1)

    def test_custom_admission_number_not_overwritten(self):
        user = make_student_user(username="customstu")
        student = Student.objects.create(
            user=user, classroom=self.classroom, admission_number="CUSTOM-001"
        )
        self.assertEqual(student.admission_number, "CUSTOM-001")

    def test_get_admission_number(self):
        user = make_student_user(username="getadmstu")
        student = Student.objects.create(user=user, classroom=self.classroom)
        self.assertEqual(student.get_admission_number(), student.admission_number)

    def test_str_contains_full_name(self):
        user = make_student_user(username="strstu")
        user.first_name = "Jane"
        user.last_name = "Doe"
        user.save()
        student = Student.objects.create(user=user, classroom=self.classroom)
        result = str(student)
        self.assertIn("Jane", result)
        self.assertIn("Doe", result)


# ---------------------------------------------------------------------------
# StudentViewSet
# ---------------------------------------------------------------------------

class StudentViewSetListTest(APITestCase):

    def setUp(self):
        self.url = "/api/students/"
        self.principal = make_principal()
        classroom = make_classroom()
        user = make_student_user(username="liststudent")
        Student.objects.create(user=user, classroom=classroom)

    def test_authenticated_can_list_students(self):
        self.client.force_authenticate(user=self.principal)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class StudentViewSetCreateTest(APITestCase):

    def setUp(self):
        self.url = "/api/students/"
        self.principal = make_principal(username="createsprincip")
        make_classroom(class_name="6th", section="A")
        make_house(house_name="Araval", house_category="Junior")

    def test_principal_can_create_student(self):
        self.client.force_authenticate(user=self.principal)
        data = {
            "username": "newstudent001",
            "first_name": "Tom",
            "last_name": "Hardy",
            "email": "tom@example.com",
            "gender": "male",
            "class_name": "6th",
            "section": "A",
            "house_name": "Araval",
            "house_category": "Junior",
            "parent_first_name": "Bob",
            "parent_last_name": "Hardy",
            "parent_phone1": "9876543210",
            "parent_email": "bob@example.com",
            "present_address": "123 Main St",
            "permanent_address": "456 Other St",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Student.objects.filter(user__username="newstudent001").exists())

    def test_duplicate_username_returns_400(self):
        self.client.force_authenticate(user=self.principal)
        data = {
            "username": "dupstudent",
            "first_name": "Tom",
            "last_name": "Hardy",
            "email": "tom2@example.com",
            "gender": "male",
            "class_name": "6th",
            "section": "A",
            "house_name": "Araval",
            "house_category": "Junior",
            "parent_first_name": "Bob",
            "parent_last_name": "Hardy",
            "parent_phone1": "9876543210",
            "parent_email": "bob2@example.com",
            "present_address": "123 Main St",
            "permanent_address": "456 Other St",
        }
        self.client.post(self.url, data, format="json")
        # Post same username again
        data["parent_email"] = "bob3@example.com"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class StudentViewSetRetrieveTest(APITestCase):

    def setUp(self):
        self.principal = make_principal(username="retrievesprincip")
        classroom = make_classroom(class_name="7th", section="B")
        user = make_student_user(username="retrievestu")
        self.student = Student.objects.create(user=user, classroom=classroom)
        self.url = f"/api/students/{self.student.pk}/"

    def test_retrieve_student_by_id(self):
        self.client.force_authenticate(user=self.principal)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_nonexistent_returns_404(self):
        self.client.force_authenticate(user=self.principal)
        response = self.client.get("/api/students/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
