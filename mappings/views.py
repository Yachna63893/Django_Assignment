from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import PatientDoctorMapping
from .serializers import (
    PatientDoctorMappingSerializer,
    AssignedDoctorSerializer,
)
from patients.models import Patient
from doctors.models import Doctor


class MappingListCreateView(generics.ListCreateAPIView):
    """
    POST /api/mappings/ - Assign a doctor to a patient
    GET /api/mappings/  - Retrieve all patient-doctor mappings
    """
    serializer_class = PatientDoctorMappingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = PatientDoctorMapping.objects.all().select_related('patient', 'doctor', 'assigned_by')
        patient_id = self.request.query_params.get('patient_id')
        doctor_id = self.request.query_params.get('doctor_id')

        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


class MappingDetailView(APIView):
    """
    Handles:
    GET /api/mappings/<patient_id>/ - Get all doctors assigned to a specific patient
    DELETE /api/mappings/<id>/      - Remove a doctor from a patient (by mapping id)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssignedDoctorSerializer

    @extend_schema(
        summary="Get doctors assigned to a patient or mapping detail",
        description="Retrieve all doctors assigned to the specified patient ID, or mapping details.",
        responses={200: AssignedDoctorSerializer(many=True)}
    )
    def get(self, request, pk, *args, **kwargs):
        # First check if pk corresponds to a patient_id
        patient = Patient.objects.filter(pk=pk).first()

        if patient:
            mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('doctor')
            serializer = AssignedDoctorSerializer(mappings, many=True)
            return Response(
                {
                    'success': True,
                    'patient_id': patient.id,
                    'patient_name': patient.name,
                    'total_assigned_doctors': mappings.count(),
                    'assigned_doctors': serializer.data,
                },
                status=status.HTTP_200_OK
            )

        # Fallback: check if pk is a mapping ID
        mapping = PatientDoctorMapping.objects.filter(pk=pk).select_related('patient', 'doctor', 'assigned_by').first()
        if mapping:
            serializer = PatientDoctorMappingSerializer(mapping)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {'detail': f'Patient or Mapping with id {pk} not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    @extend_schema(
        summary="Remove doctor from patient",
        description="Delete a patient-doctor mapping by mapping ID or patient ID with doctor_id in body/param.",
        responses={200: OpenApiResponse(description="Doctor removed successfully.")}
    )
    def delete(self, request, pk, *args, **kwargs):
        # Attempt to delete by mapping ID first
        mapping = PatientDoctorMapping.objects.filter(pk=pk).first()

        if mapping:
            patient_name = mapping.patient.name
            doctor_name = mapping.doctor.name
            mapping.delete()
            return Response(
                {
                    'success': True,
                    'message': f"Doctor '{doctor_name}' successfully removed from patient '{patient_name}'."
                },
                status=status.HTTP_200_OK
            )

        # If not found by mapping ID, check if pk is patient_id and doctor_id was provided
        doctor_id = request.data.get('doctor_id') or request.query_params.get('doctor_id')
        if doctor_id:
            mapping = PatientDoctorMapping.objects.filter(patient_id=pk, doctor_id=doctor_id).first()
            if mapping:
                patient_name = mapping.patient.name
                doctor_name = mapping.doctor.name
                mapping.delete()
                return Response(
                    {
                        'success': True,
                        'message': f"Doctor '{doctor_name}' successfully removed from patient '{patient_name}'."
                    },
                    status=status.HTTP_200_OK
                )

        return Response(
            {'detail': f'Mapping with id {pk} not found.'},
            status=status.HTTP_404_NOT_FOUND
        )


class PatientAssignedDoctorsExplicitView(APIView):
    """
    GET /api/mappings/patient/<patient_id>/
    Explicit endpoint for retrieving all doctors assigned to a specific patient.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssignedDoctorSerializer

    @extend_schema(
        summary="Explicitly get doctors assigned to a patient",
        description="Returns all doctors assigned to the specified patient ID.",
        responses={200: AssignedDoctorSerializer(many=True)}
    )
    def get(self, request, patient_id, *args, **kwargs):
        patient = get_object_or_404(Patient, pk=patient_id)
        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('doctor')
        serializer = AssignedDoctorSerializer(mappings, many=True)
        return Response(
            {
                'success': True,
                'patient_id': patient.id,
                'patient_name': patient.name,
                'total_assigned_doctors': mappings.count(),
                'assigned_doctors': serializer.data,
            },
            status=status.HTTP_200_OK
        )


class RemoveMappingExplicitView(APIView):
    """
    DELETE /api/mappings/remove/<patient_id>/<doctor_id>/
    Remove a mapping by explicit patient_id and doctor_id.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Explicitly remove mapping by patient and doctor ID",
        description="Deletes mapping between specified patient and doctor.",
        responses={200: OpenApiResponse(description="Doctor unassigned successfully.")}
    )
    def delete(self, request, patient_id, doctor_id, *args, **kwargs):
        mapping = PatientDoctorMapping.objects.filter(patient_id=patient_id, doctor_id=doctor_id).first()
        if not mapping:
            return Response(
                {'detail': 'Mapping between specified patient and doctor does not exist.'},
                status=status.HTTP_404_NOT_FOUND
            )

        patient_name = mapping.patient.name
        doctor_name = mapping.doctor.name
        mapping.delete()

        return Response(
            {
                'success': True,
                'message': f"Doctor '{doctor_name}' successfully removed from patient '{patient_name}'."
            },
            status=status.HTTP_200_OK
        )
