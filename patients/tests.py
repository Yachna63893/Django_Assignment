from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Patient

User = get_user_model()


class PatientAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            name='User One',
            password='Password123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            name='User Two',
            password='Password123'
        )

        self.list_create_url = reverse('patients:patient-list-create')

        self.patient_data = {
            'name': 'John Doe',
            'age': 45,
            'gender': 'Male',
            'contact_number': '+1-555-0199',
            'email': 'john.doe@example.com',
            'address': '123 Health Ave, Metropolis',
            'medical_history': 'Hypertension diagnosed in 2020.'
        }

    def test_create_patient_unauthenticated_fails(self):
        response = self.client.post(self.list_create_url, self.patient_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_patient_authenticated_success(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.list_create_url, self.patient_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'John Doe')
        self.assertEqual(response.data['created_by'], self.user1.id)

    def test_list_patients_isolated_to_creator(self):
        # Patient created by user1
        p1 = Patient.objects.create(
            name='Patient One',
            age=30,
            gender='Female',
            contact_number='1234567890',
            created_by=self.user1
        )
        # Patient created by user2
        p2 = Patient.objects.create(
            name='Patient Two',
            age=40,
            gender='Male',
            contact_number='0987654321',
            created_by=self.user2
        )

        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Results should only contain p1
        patient_names = [p['name'] for p in response.data]
        self.assertIn('Patient One', patient_names)
        self.assertNotIn('Patient Two', patient_names)

    def test_get_patient_details(self):
        p1 = Patient.objects.create(
            name='Jane Smith',
            age=28,
            gender='Female',
            contact_number='1234567890',
            created_by=self.user1
        )
        detail_url = reverse('patients:patient-detail', kwargs={'pk': p1.id})
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Jane Smith')

    def test_update_patient(self):
        p1 = Patient.objects.create(
            name='Jane Smith',
            age=28,
            gender='Female',
            contact_number='1234567890',
            created_by=self.user1
        )
        detail_url = reverse('patients:patient-detail', kwargs={'pk': p1.id})
        self.client.force_authenticate(user=self.user1)
        update_data = {
            'name': 'Jane Doe',
            'age': 29,
            'gender': 'Female',
            'contact_number': '1234567890',
        }
        response = self.client.put(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        p1.refresh_from_db()
        self.assertEqual(p1.name, 'Jane Doe')
        self.assertEqual(p1.age, 29)

    def test_delete_patient(self):
        p1 = Patient.objects.create(
            name='To Be Deleted',
            age=50,
            gender='Male',
            contact_number='1234567890',
            created_by=self.user1
        )
        detail_url = reverse('patients:patient-detail', kwargs={'pk': p1.id})
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Patient.objects.filter(id=p1.id).exists())
