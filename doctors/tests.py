from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Doctor

User = get_user_model()


class DoctorAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='doctor_admin@test.com',
            name='Hospital Admin',
            password='AdminPassword123'
        )
        self.list_create_url = reverse('doctors:doctor-list-create')
        self.doctor_data = {
            'name': 'Gregory House',
            'specialization': 'Diagnostic Medicine',
            'contact_number': '+1-555-0144',
            'email': 'gregory.house@ppth.test',
            'experience_years': 20,
            'hospital_affiliation': 'Princeton-Plainsboro'
        }

    def test_create_doctor_unauthenticated_fails(self):
        response = self.client.post(self.list_create_url, self.doctor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_doctor_authenticated_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_create_url, self.doctor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Gregory House')
        self.assertTrue(Doctor.objects.filter(email='gregory.house@ppth.test').exists())

    def test_list_all_doctors(self):
        Doctor.objects.create(
            name='Dr. Allison Cameron',
            specialization='Immunology',
            contact_number='1234567890',
            email='cameron@ppth.test',
            experience_years=8
        )
        Doctor.objects.create(
            name='Dr. Robert Chase',
            specialization='Intensive Care',
            contact_number='1234567891',
            email='chase@ppth.test',
            experience_years=9
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_doctor_details(self):
        doc = Doctor.objects.create(
            name='Dr. James Wilson',
            specialization='Oncology',
            contact_number='1234567892',
            email='wilson@ppth.test',
            experience_years=15
        )
        detail_url = reverse('doctors:doctor-detail', kwargs={'pk': doc.id})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['specialization'], 'Oncology')

    def test_update_doctor(self):
        doc = Doctor.objects.create(
            name='Dr. Eric Foreman',
            specialization='Neurology',
            contact_number='1234567893',
            email='foreman@ppth.test',
            experience_years=10
        )
        detail_url = reverse('doctors:doctor-detail', kwargs={'pk': doc.id})
        self.client.force_authenticate(user=self.user)
        updated_payload = {
            'name': 'Dr. Eric Foreman',
            'specialization': 'Chief of Medicine',
            'contact_number': '1234567893',
            'email': 'foreman@ppth.test',
            'experience_years': 12,
            'hospital_affiliation': 'PPTH'
        }
        response = self.client.put(detail_url, updated_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doc.refresh_from_db()
        self.assertEqual(doc.specialization, 'Chief of Medicine')

    def test_delete_doctor(self):
        doc = Doctor.objects.create(
            name='Temporary Doctor',
            specialization='General',
            contact_number='1234567894',
            email='temp@ppth.test',
            experience_years=1
        )
        detail_url = reverse('doctors:doctor-detail', kwargs={'pk': doc.id})
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Doctor.objects.filter(id=doc.id).exists())
