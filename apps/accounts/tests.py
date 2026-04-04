from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.accounts.models import User, PrincipalProfile


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_principal(username="principal1", password="pass1234"):
    user = User.objects.create_user(
        username=username, password=password, role="principal"
    )
    return user


def make_teacher(username="teacher1", password="pass1234"):
    return User.objects.create_user(
        username=username, password=password, role="teacher"
    )


def make_student(username="student1", password="pass1234"):
    return User.objects.create_user(
        username=username, password=password, role="student"
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class UserModelTest(TestCase):

    def test_str_returns_username(self):
        user = User(username="john")
        self.assertEqual(str(user), "john")

    def test_default_role_is_principal(self):
        user = User.objects.create_user(username="u1", password="p")
        self.assertEqual(user.role, "principal")

    def test_default_gender_is_male(self):
        user = User.objects.create_user(username="u2", password="p")
        self.assertEqual(user.gender, "male")

    def test_can_set_role(self):
        user = User.objects.create_user(username="u3", password="p", role="teacher")
        self.assertEqual(user.role, "teacher")


class PrincipalProfileModelTest(TestCase):

    def test_profile_auto_created_for_principal(self):
        user = make_principal(username="prin1")
        self.assertTrue(hasattr(user, "principal_profile"))
        self.assertIsInstance(user.principal_profile, PrincipalProfile)

    def test_profile_not_auto_created_for_non_principal(self):
        user = make_teacher(username="teach1")
        self.assertFalse(hasattr(user, "principal_profile"))

    def test_str_contains_username(self):
        user = make_principal(username="prin2")
        self.assertIn("prin2", str(user.principal_profile))

    def test_get_full_name(self):
        user = make_principal(username="prin3")
        user.first_name = "Alice"
        user.last_name = "Smith"
        user.save()
        self.assertEqual(user.principal_profile.get_full_name(), "Alice Smith")


# ---------------------------------------------------------------------------
# Login view
# ---------------------------------------------------------------------------

class LoginViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("login")
        self.user = make_principal(username="loginuser", password="testpass123")

    def test_valid_credentials_return_tokens(self):
        data = {"username": "loginuser", "password": "testpass123"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

    def test_valid_login_returns_user_info(self):
        data = {"username": "loginuser", "password": "testpass123"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.data["user"]["username"], "loginuser")
        self.assertEqual(response.data["user"]["role"], "principal")

    def test_invalid_password_returns_400(self):
        data = {"username": "loginuser", "password": "wrongpassword"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_user_returns_400(self):
        data = {"username": "nobody", "password": "testpass123"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_user_returns_400(self):
        self.user.is_active = False
        self.user.save()
        data = {"username": "loginuser", "password": "testpass123"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_username_returns_400(self):
        response = self.client.post(self.url, {"password": "testpass123"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_password_returns_400(self):
        response = self.client.post(self.url, {"username": "loginuser"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# Me view
# ---------------------------------------------------------------------------

class MeViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("me")
        self.user = make_principal(username="meuser", password="pass1234")

    def test_authenticated_returns_user_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "meuser")

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ---------------------------------------------------------------------------
# Update principal profile view
# ---------------------------------------------------------------------------

class UpdatePrincipalProfileViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("update-principal-profile")
        self.principal = make_principal(username="principalup", password="pass1234")
        self.teacher = make_teacher(username="teacherup", password="pass1234")

    def test_principal_can_update_profile(self):
        self.client.force_authenticate(user=self.principal)
        response = self.client.put(self.url, {"bio": "School principal"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_cannot_update_principal_profile(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.put(self.url, {"bio": "Trying to update"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_returns_401(self):
        response = self.client.put(self.url, {"bio": "No auth"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_first_last_name(self):
        self.client.force_authenticate(user=self.principal)
        response = self.client.put(
            self.url,
            {"first_name": "New", "last_name": "Name"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.principal.refresh_from_db()
        self.assertEqual(self.principal.first_name, "New")
        self.assertEqual(self.principal.last_name, "Name")


# ---------------------------------------------------------------------------
# Change password view
# ---------------------------------------------------------------------------

class ChangePasswordViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("change-password")
        self.user = make_principal(username="pwuser", password="oldpass123")

    def test_correct_current_password_updates_password(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(
            self.url,
            {"current_password": "oldpass123", "new_password": "newpass456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass456"))

    def test_wrong_current_password_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(
            self.url,
            {"current_password": "wrongpassword", "new_password": "newpass456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_returns_401(self):
        response = self.client.put(
            self.url,
            {"current_password": "oldpass123", "new_password": "newpass456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
