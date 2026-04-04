from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from apps.accounts.models import User
from apps.parents.models import Parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_principal(username="parprincip", password="pass1234"):
    return User.objects.create_user(username=username, password=password, role="principal")


def make_parent_user(username="paruser1", password="pass1234"):
    return User.objects.create_user(username=username, password=password, role="parent")


def make_parent(username="parprofile1", password="pass1234"):
    user = make_parent_user(username=username, password=password)
    return Parent.objects.create(
        user=user,
        first_name="David",
        last_name="Green",
        phone1="9000000001",
        email="david@example.com",
        present_address="100 Park Ave",
        permanent_address="200 Park Ave",
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class ParentModelTest(TestCase):

    def test_str_returns_email(self):
        user = make_parent_user(username="strparent")
        parent = Parent(user=user, email="test@email.com", first_name="A",
                        last_name="B", phone1="123", present_address="X",
                        permanent_address="Y")
        self.assertEqual(str(parent), "test@email.com")

    def test_get_full_name(self):
        user = make_parent_user(username="fullnameparent")
        parent = Parent(user=user, first_name="Mary", last_name="Jane",
                        email="mj@example.com", phone1="123",
                        present_address="X", permanent_address="Y")
        self.assertEqual(parent.get_full_name(), "Mary Jane")


# ---------------------------------------------------------------------------
# ParentViewset (principal only)
# ---------------------------------------------------------------------------

class ParentViewsetTest(APITestCase):

    def setUp(self):
        self.list_url = "/api/parents/parents/"
        self.principal = make_principal()
        self.parent = make_parent()

    def test_principal_can_list_parents(self):
        self.client.force_authenticate(user=self.principal)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_principal_returns_403(self):
        self.client.force_authenticate(user=self.parent.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_principal_can_retrieve_parent(self):
        self.client.force_authenticate(user=self.principal)
        url = f"/api/parents/parents/{self.parent.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "david@example.com")


# ---------------------------------------------------------------------------
# ParentProfileview
# ---------------------------------------------------------------------------

class ParentProfileViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("parent-profile")
        self.parent = make_parent(username="profileparent")
        self.principal = make_principal(username="profparentprincip")

    def test_parent_can_view_own_profile(self):
        self.client.force_authenticate(user=self.parent.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "david@example.com")

    def test_parent_can_patch_own_profile(self):
        self.client.force_authenticate(user=self.parent.user)
        response = self.client.patch(
            self.url, {"first_name": "Updated"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.parent.refresh_from_db()
        self.assertEqual(self.parent.first_name, "Updated")

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
