from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from patients.models import Patient
from doctors.models import Doctor
from .models import PatientDoctorMapping

User = get_user_model()


class MappingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='coordinator@hospital.test',
            name='Clinical Coordinator',
            password='Password123'
        )
        self.client.force_authenticate(user=self.user)

        self.patient = Patient.objects.create(
            name='Bruce Wayne',
            age=35,
            gender='Male',
            contact_number='1234567890',
            created_by=self.user
        )

        self.doctor1 = Doctor.objects.create(
            name='Dr. Thomas Elliot',
            specialization='Brain Surgery',
            contact_number='1112223333',
            email='elliot@hospital.test',
            experience_years=14
        )

        self.doctor2 = Doctor.objects.create(
            name='Dr. Leslie Thompkins',
            specialization='General Practice',
            contact_number='2223334444',
            email='thompkins@clinic.test',
            experience_years=30
        )

        self.mapping_list_create_url = reverse('mappings:mapping-list-create')

    def test_assign_doctor_to_patient_success(self):
        payload = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor1.id,
            'notes': 'Referred for neurological assessment.'
        }
        response = self.client.post(self.mapping_list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PatientDoctorMapping.objects.filter(patient=self.patient, doctor=self.doctor1).exists())

    def test_duplicate_assignment_fails(self):
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor1,
            assigned_by=self.user
        )
        payload = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor1.id,
        }
        response = self.client.post(self.mapping_list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_mappings(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1, assigned_by=self.user)
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor2, assigned_by=self.user)

        response = self.client.get(self.mapping_list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_doctors_assigned_to_patient(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1, assigned_by=self.user)
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor2, assigned_by=self.user)

        # GET /api/mappings/<patient_id>/
        url = reverse('mappings:mapping-detail', kwargs={'pk': self.patient.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['patient_id'], self.patient.id)
        self.assertEqual(response.data['total_assigned_doctors'], 2)
        doctor_names = [d['doctor_name'] for d in response.data['assigned_doctors']]
        self.assertIn('Dr. Thomas Elliot', doctor_names)
        self.assertIn('Dr. Leslie Thompkins', doctor_names)

    def test_remove_doctor_from_patient(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor1,
            assigned_by=self.user
        )
        # DELETE /api/mappings/<id>/
        delete_url = reverse('mappings:mapping-detail', kwargs={'pk': mapping.id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PatientDoctorMapping.objects.filter(id=mapping.id).exists())
