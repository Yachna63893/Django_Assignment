from rest_framework import serializers
from .models import PatientDoctorMapping
from patients.models import Patient
from doctors.models import Doctor


class NestedPatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'name', 'age', 'gender', 'contact_number', 'email')


class NestedDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('id', 'name', 'specialization', 'contact_number', 'email', 'experience_years', 'hospital_affiliation')


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        source='doctor',
        write_only=True
    )

    # Read representations
    patient = NestedPatientSerializer(read_only=True)
    doctor = NestedDoctorSerializer(read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.name', read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = (
            'id',
            'patient_id',
            'doctor_id',
            'patient',
            'doctor',
            'notes',
            'assigned_by',
            'assigned_by_name',
            'assigned_at',
        )
        read_only_fields = ('id', 'assigned_by', 'assigned_at')

    def validate(self, attrs):
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')

        # Check for duplicate mapping
        if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError(
                f"Doctor '{doctor.name}' is already assigned to patient '{patient.name}'."
            )

        return attrs


class AssignedDoctorSerializer(serializers.Serializer):
    mapping_id = serializers.IntegerField(source='id')
    doctor_id = serializers.IntegerField(source='doctor.id')
    doctor_name = serializers.CharField(source='doctor.name')
    specialization = serializers.CharField(source='doctor.specialization')
    contact_number = serializers.CharField(source='doctor.contact_number')
    email = serializers.EmailField(source='doctor.email')
    experience_years = serializers.IntegerField(source='doctor.experience_years')
    hospital_affiliation = serializers.CharField(source='doctor.hospital_affiliation')
    notes = serializers.CharField()
    assigned_at = serializers.DateTimeField()
