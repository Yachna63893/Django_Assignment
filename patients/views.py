from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Patient
from .serializers import PatientSerializer
from .permissions import IsOwnerOrStaff


class PatientListCreateView(generics.ListCreateAPIView):
    """
    POST /api/patients/ - Add a new patient (Authenticated users only)
    GET /api/patients/  - Retrieve all patients created by the authenticated user
    """
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Staff can view all, regular users view only their own created patients
        if self.request.user.is_staff:
            return Patient.objects.all()
        return Patient.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/patients/<id>/    - Get details of a specific patient
    PUT /api/patients/<id>/    - Update patient details (Creator/Admin)
    PATCH /api/patients/<id>/  - Partially update patient details (Creator/Admin)
    DELETE /api/patients/<id>/ - Delete a patient record (Creator/Admin)
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        patient_name = instance.name
        self.perform_destroy(instance)
        return Response(
            {
                'success': True,
                'message': f"Patient '{patient_name}' deleted successfully."
            },
            status=status.HTTP_200_OK
        )
