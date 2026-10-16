from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from patients.models import Patient
from doctors.models import Doctor
from mappings.models import PatientDoctorMapping

User = get_user_model()


class Command(BaseCommand):
    help = 'Populates the database with realistic healthcare sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting healthcare data seeding...'))

        # 1. Create Superuser / Admin
        admin_email = 'admin@healthcare.test'
        admin_user, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'name': 'System Administrator',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        if created:
            admin_user.set_password('Admin@12345')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"Created Superuser: {admin_email} / Admin@12345"))
        else:
            self.stdout.write(f"Superuser {admin_email} already exists.")

        # 2. Create Regular Healthcare Staff User
        staff_email = 'staff@healthcare.test'
        staff_user, created = User.objects.get_or_create(
            email=staff_email,
            defaults={
                'name': 'Nurse Sarah Connor',
                'is_active': True,
            }
        )
        if created:
            staff_user.set_password('Staff@12345')
            staff_user.save()
            self.stdout.write(self.style.SUCCESS(f"Created Staff User: {staff_email} / Staff@12345"))
        else:
            self.stdout.write(f"Staff User {staff_email} already exists.")

        # 3. Create Sample Doctors
        doctors_data = [
            {
                'name': 'Dr. Sarah Johnson',
                'specialization': 'Cardiology',
                'contact_number': '+1-555-0101',
                'email': 'sarah.johnson@hospital.test',
                'experience_years': 12,
                'hospital_affiliation': 'Heart & Vascular Institute',
            },
            {
                'name': 'Dr. Michael Chen',
                'specialization': 'Neurology',
                'contact_number': '+1-555-0102',
                'email': 'michael.chen@hospital.test',
                'experience_years': 15,
                'hospital_affiliation': 'City General Hospital',
            },
            {
                'name': 'Dr. Emily Davis',
                'specialization': 'Pediatrics',
                'contact_number': '+1-555-0103',
                'email': 'emily.davis@hospital.test',
                'experience_years': 8,
                'hospital_affiliation': "Children's Medical Care",
            },
        ]

        doctors = []
        for d_data in doctors_data:
            doc, created = Doctor.objects.get_or_create(
                email=d_data['email'],
                defaults={**d_data, 'created_by': staff_user}
            )
            doctors.append(doc)
            status_text = 'Created' if created else 'Existing'
            self.stdout.write(f"{status_text} Doctor: {doc.name} ({doc.specialization})")

        # 4. Create Sample Patients
        patients_data = [
            {
                'name': 'Robert Miller',
                'age': 52,
                'gender': 'Male',
                'contact_number': '+1-555-0201',
                'email': 'robert.miller@patient.test',
                'address': '45 Elm Street, Springfield',
                'medical_history': 'Stage 1 Hypertension, elevated cholesterol.',
                'created_by': staff_user
            },
            {
                'name': 'Alice Smith',
                'age': 34,
                'gender': 'Female',
                'contact_number': '+1-555-0202',
                'email': 'alice.smith@patient.test',
                'address': '782 Maple Avenue, Springfield',
                'medical_history': 'Chronic migraine, mild asthma.',
                'created_by': staff_user
            },
        ]

        patients = []
        for p_data in patients_data:
            p, created = Patient.objects.get_or_create(
                name=p_data['name'],
                created_by=staff_user,
                defaults=p_data
            )
            patients.append(p)
            status_text = 'Created' if created else 'Existing'
            self.stdout.write(f"{status_text} Patient: {p.name}")

        # 5. Create Patient-Doctor Mappings
        if len(patients) >= 2 and len(doctors) >= 2:
            # Assign Dr. Sarah Johnson and Dr. Michael Chen to Robert Miller
            m1, c1 = PatientDoctorMapping.objects.get_or_create(
                patient=patients[0],
                doctor=doctors[0],
                defaults={'notes': 'Cardiovascular review and monitoring', 'assigned_by': staff_user}
            )
            m2, c2 = PatientDoctorMapping.objects.get_or_create(
                patient=patients[0],
                doctor=doctors[1],
                defaults={'notes': 'Neurological consult for dizzy spells', 'assigned_by': staff_user}
            )
            # Assign Dr. Emily Davis to Alice Smith
            m3, c3 = PatientDoctorMapping.objects.get_or_create(
                patient=patients[1],
                doctor=doctors[2],
                defaults={'notes': 'Routine allergy and pediatric follow-up', 'assigned_by': staff_user}
            )
            self.stdout.write(self.style.SUCCESS("Patient-Doctor mappings seeded successfully."))

        self.stdout.write(self.style.SUCCESS("\nSample data seeded successfully!"))
