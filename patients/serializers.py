import re
from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)

    class Meta:
        model = Patient
        fields = (
            'id',
            'name',
            'age',
            'gender',
            'contact_number',
            'email',
            'address',
            'medical_history',
            'created_by',
            'created_by_name',
            'created_by_email',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def validate_name(self, value):
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError("Patient name cannot be empty.")
        return trimmed

    def validate_age(self, value):
        if value < 0 or value > 150:
            raise serializers.ValidationError("Age must be between 0 and 150.")
        return value

    def validate_contact_number(self, value):
        trimmed = value.strip()
        # Ensure it contains valid characters like +, digits, dashes, spaces
        cleaned = re.sub(r'[\s\-\(\)\+]', '', trimmed)
        if not cleaned.isdigit() or len(cleaned) < 7 or len(cleaned) > 15:
            raise serializers.ValidationError("Please provide a valid contact number (7 to 15 digits).")
        return trimmed

    def validate_gender(self, value):
        valid_genders = ['Male', 'Female', 'Other']
        if value.capitalize() not in valid_genders:
            raise serializers.ValidationError(f"Gender must be one of: {', '.join(valid_genders)}")
        return value.capitalize()
