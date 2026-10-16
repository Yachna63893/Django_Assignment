"""
End-to-end API verification script for Healthcare Backend
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare_project.settings')
django.setup()

from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


def run_verification():
    print("=" * 60)
    print("HEALTHCARE BACKEND END-TO-END VERIFICATION")
    print("=" * 60)

    client = APIClient()

    # 1. Register a new user
    print("\n[Step 1] Testing User Registration (/api/auth/register/)")
    reg_payload = {
        'name': 'Dr. Gregory House',
        'email': 'house.verify@ppth.test',
        'password': 'ComplexPassword123!'
    }
    # Clean up if exists
    User.objects.filter(email=reg_payload['email']).delete()

    res = client.post('/api/auth/register/', reg_payload, format='json')
    assert res.status_code == status.HTTP_201_CREATED, f"Registration failed: {res.data}"
    print(f"  [PASS] User registered successfully! ID: {res.data['user']['id']}")
    tokens = res.data.get('tokens', {})
    access_token = tokens.get('access')

    # 2. Login user
    print("\n[Step 2] Testing User Login (/api/auth/login/)")
    login_payload = {
        'email': reg_payload['email'],
        'password': reg_payload['password']
    }
    res = client.post('/api/auth/login/', login_payload, format='json')
    assert res.status_code == status.HTTP_200_OK, f"Login failed: {res.data}"
    access_token = res.data['access']
    print(f"  [PASS] Login successful! JWT Access Token received.")

    # Set auth header
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # 3. Add a patient
    print("\n[Step 3] Testing Add Patient (POST /api/patients/)")
    patient_payload = {
        'name': 'Arthur Dent',
        'age': 38,
        'gender': 'Male',
        'contact_number': '+44-20-7946-0919',
        'email': 'arthur.dent@galaxy.test',
        'address': 'West Country, England',
        'medical_history': 'Frequent bouts of cosmic motion sickness.'
    }
    res = client.post('/api/patients/', patient_payload, format='json')
    assert res.status_code == status.HTTP_201_CREATED, f"Create patient failed: {res.data}"
    patient_id = res.data['id']
    print(f"  [PASS] Patient created! ID: {patient_id}, Name: {res.data['name']}")

    # 4. Get patient list
    print("\n[Step 4] Testing Get Patient List (GET /api/patients/)")
    res = client.get('/api/patients/')
    assert res.status_code == status.HTTP_200_OK, f"Get patients failed: {res.data}"
    patient_ids = [p['id'] for p in res.data]
    assert patient_id in patient_ids, "Created patient not found in list"
    print(f"  [PASS] Successfully retrieved {len(res.data)} patient(s) created by this user.")

    # 5. Get patient details
    print(f"\n[Step 5] Testing Get Patient Detail (GET /api/patients/{patient_id}/)")
    res = client.get(f'/api/patients/{patient_id}/')
    assert res.status_code == status.HTTP_200_OK, f"Get patient detail failed: {res.data}"
    print(f"  [PASS] Patient detail retrieved: {res.data['name']} (Age: {res.data['age']})")

    # 6. Update patient
    print(f"\n[Step 6] Testing Update Patient (PUT /api/patients/{patient_id}/)")
    update_patient_payload = {
        'name': 'Arthur Dent (Updated)',
        'age': 39,
        'gender': 'Male',
        'contact_number': '+44-20-7946-0919',
        'email': 'arthur.dent@galaxy.test',
        'address': 'Earth (Mark II)',
        'medical_history': 'Recovered from panic attacks.'
    }
    res = client.put(f'/api/patients/{patient_id}/', update_patient_payload, format='json')
    assert res.status_code == status.HTTP_200_OK, f"Update patient failed: {res.data}"
    assert res.data['name'] == 'Arthur Dent (Updated)'
    print(f"  [PASS] Patient updated successfully: {res.data['name']}")

    # 7. Add a doctor
    print("\n[Step 7] Testing Add Doctor (POST /api/doctors/)")
    doctor_payload = {
        'name': 'Dr. Leonard McCoy',
        'specialization': 'Exobiology & Emergency Surgery',
        'contact_number': '+1-555-0170',
        'email': 'mccoy.verify@enterprise.test',
        'experience_years': 25,
        'hospital_affiliation': 'Starfleet Medical'
    }
    # Clean up if doctor exists
    from doctors.models import Doctor
    Doctor.objects.filter(email=doctor_payload['email']).delete()

    res = client.post('/api/doctors/', doctor_payload, format='json')
    assert res.status_code == status.HTTP_201_CREATED, f"Add doctor failed: {res.data}"
    doctor_id = res.data['id']
    print(f"  [PASS] Doctor created! ID: {doctor_id}, Name: {res.data['name']}")

    # 8. Get all doctors
    print("\n[Step 8] Testing Get All Doctors (GET /api/doctors/)")
    res = client.get('/api/doctors/')
    assert res.status_code == status.HTTP_200_OK, f"Get doctors failed: {res.data}"
    doctor_ids = [d['id'] for d in res.data]
    assert doctor_id in doctor_ids
    print(f"  [PASS] Successfully retrieved {len(res.data)} total doctor(s).")

    # 9. Get doctor details
    print(f"\n[Step 9] Testing Get Doctor Detail (GET /api/doctors/{doctor_id}/)")
    res = client.get(f'/api/doctors/{doctor_id}/')
    assert res.status_code == status.HTTP_200_OK, f"Get doctor detail failed: {res.data}"
    print(f"  [PASS] Doctor details retrieved: {res.data['name']} - {res.data['specialization']}")

    # 10. Update doctor
    print(f"\n[Step 10] Testing Update Doctor (PUT /api/doctors/{doctor_id}/)")
    update_doc_payload = {
        'name': 'Dr. Leonard McCoy (Chief Medical Officer)',
        'specialization': 'Exobiology & Trauma Medicine',
        'contact_number': '+1-555-0170',
        'email': 'mccoy.verify@enterprise.test',
        'experience_years': 26,
        'hospital_affiliation': 'USS Enterprise NCC-1701'
    }
    res = client.put(f'/api/doctors/{doctor_id}/', update_doc_payload, format='json')
    assert res.status_code == status.HTTP_200_OK, f"Update doctor failed: {res.data}"
    print(f"  [PASS] Doctor updated: {res.data['name']}")

    # 11. Assign doctor to patient (POST /api/mappings/)
    print("\n[Step 11] Testing Assign Doctor to Patient (POST /api/mappings/)")
    mapping_payload = {
        'patient_id': patient_id,
        'doctor_id': doctor_id,
        'notes': 'Primary physician for space expedition medical clearance.'
    }
    res = client.post('/api/mappings/', mapping_payload, format='json')
    assert res.status_code == status.HTTP_201_CREATED, f"Mapping failed: {res.data}"
    mapping_id = res.data['id']
    print(f"  [PASS] Doctor assigned to Patient successfully! Mapping ID: {mapping_id}")

    # 12. Duplicate assignment prevention test
    print("\n[Step 12] Testing Duplicate Assignment Validation")
    res = client.post('/api/mappings/', mapping_payload, format='json')
    assert res.status_code == status.HTTP_400_BAD_REQUEST, "Duplicate mapping was unexpectedly allowed!"
    print(f"  [PASS] Correctly rejected duplicate assignment with status 400.")

    # 13. Get all mappings
    print("\n[Step 13] Testing Retrieve All Mappings (GET /api/mappings/)")
    res = client.get('/api/mappings/')
    assert res.status_code == status.HTTP_200_OK, f"Get mappings failed: {res.data}"
    print(f"  [PASS] Retrieved {len(res.data)} total mapping(s).")

    # 14. Get all doctors assigned to a specific patient
    print(f"\n[Step 14] Testing Get Doctors Assigned to Patient (GET /api/mappings/{patient_id}/)")
    res = client.get(f'/api/mappings/{patient_id}/')
    assert res.status_code == status.HTTP_200_OK, f"Get patient doctors failed: {res.data}"
    assert res.data['total_assigned_doctors'] >= 1
    print(f"  [PASS] Patient '{res.data['patient_name']}' has {res.data['total_assigned_doctors']} assigned doctor(s).")

    # 15. Remove doctor from patient
    print(f"\n[Step 15] Testing Remove Doctor from Patient (DELETE /api/mappings/{mapping_id}/)")
    res = client.delete(f'/api/mappings/{mapping_id}/')
    assert res.status_code == status.HTTP_200_OK, f"Delete mapping failed: {res.data}"
    print(f"  [PASS] Mapping removed: {res.data['message']}")

    # 16. Delete doctor
    print(f"\n[Step 16] Testing Delete Doctor (DELETE /api/doctors/{doctor_id}/)")
    res = client.delete(f'/api/doctors/{doctor_id}/')
    assert res.status_code == status.HTTP_200_OK, f"Delete doctor failed: {res.data}"
    print(f"  [PASS] Doctor deleted: {res.data['message']}")

    # 17. Delete patient
    print(f"\n[Step 17] Testing Delete Patient (DELETE /api/patients/{patient_id}/)")
    res = client.delete(f'/api/patients/{patient_id}/')
    assert res.status_code == status.HTTP_200_OK, f"Delete patient failed: {res.data}"
    print(f"  [PASS] Patient deleted: {res.data['message']}")

    print("\n" + "=" * 60)
    print("ALL 17 VERIFICATION STEPS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == '__main__':
    run_verification()
