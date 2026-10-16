from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AuthenticationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('authentication:register')
        self.login_url = reverse('authentication:login')
        self.profile_url = reverse('authentication:profile')

        self.valid_user_data = {
            'name': 'Dr. Alice Morgan',
            'email': 'alice.morgan@healthcare.test',
            'password': 'SecurePassword123'
        }

    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['user']['email'], self.valid_user_data['email'])
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertTrue(User.objects.filter(email=self.valid_user_data['email']).exists())

    def test_register_duplicate_email_fails(self):
        User.objects.create_user(
            email=self.valid_user_data['email'],
            name=self.valid_user_data['name'],
            password=self.valid_user_data['password']
        )
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)

    def test_register_short_password_fails(self):
        invalid_data = self.valid_user_data.copy()
        invalid_data['password'] = '123'
        response = self.client.post(self.register_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_success(self):
        user = User.objects.create_user(
            email=self.valid_user_data['email'],
            name=self.valid_user_data['name'],
            password=self.valid_user_data['password']
        )
        login_data = {
            'email': self.valid_user_data['email'],
            'password': self.valid_user_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_password_fails(self):
        User.objects.create_user(
            email=self.valid_user_data['email'],
            name=self.valid_user_data['name'],
            password=self.valid_user_data['password']
        )
        login_data = {
            'email': self.valid_user_data['email'],
            'password': 'WrongPassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_authenticated_access(self):
        user = User.objects.create_user(
            email=self.valid_user_data['email'],
            name=self.valid_user_data['name'],
            password=self.valid_user_data['password']
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], user.email)

    def test_profile_unauthenticated_fails(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
