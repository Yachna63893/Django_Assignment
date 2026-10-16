import re
from rest_framework import serializers
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = Doctor
        fields = (
            'id',
            'name',
            'specialization',
            'contact_number',
            'email',
            'experience_years',
            'hospital_affiliation',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def validate_name(self, value):
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError("Doctor name cannot be empty.")
        return trimmed

    def validate_specialization(self, value):
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError("Specialization cannot be empty.")
        return trimmed

    def validate_email(self, value):
        normalized = value.lower().strip()
        # Check uniqueness on update vs create
        doctor_id = self.instance.id if self.instance else None
        if Doctor.objects.filter(email=normalized).exclude(id=doctor_id).exists():
            raise serializers.ValidationError("A doctor with this email already exists.")
        return normalized

    def validate_contact_number(self, value):
        trimmed = value.strip()
        cleaned = re.sub(r'[\s\-\(\)\+]', '', trimmed)
        if not cleaned.isdigit() or len(cleaned) < 7 or len(cleaned) > 15:
            raise serializers.ValidationError("Please provide a valid contact number (7 to 15 digits).")
        return trimmed

    def validate_experience_years(self, value):
        if value < 0 or value > 80:
            raise serializers.ValidationError("Experience years must be between 0 and 80.")
        return value
