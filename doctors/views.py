from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Doctor
from .serializers import DoctorSerializer


class DoctorListCreateView(generics.ListCreateAPIView):
    """
    POST /api/doctors/ - Add a new doctor (Authenticated users only)
    GET /api/doctors/  - Retrieve all doctors
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/doctors/<id>/    - Get details of a specific doctor
    PUT /api/doctors/<id>/    - Update doctor details
    PATCH /api/doctors/<id>/  - Partially update doctor details
    DELETE /api/doctors/<id>/ - Delete a doctor record
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        doctor_name = instance.name
        self.perform_destroy(instance)
        return Response(
            {
                'success': True,
                'message': f"Doctor '{doctor_name}' deleted successfully."
            },
            status=status.HTTP_200_OK
        )
