from django.urls import path
from .views import (
    MappingListCreateView,
    MappingDetailView,
    PatientAssignedDoctorsExplicitView,
    RemoveMappingExplicitView,
)

app_name = 'mappings'

urlpatterns = [
    path('', MappingListCreateView.as_view(), name='mapping-list-create'),
    path('<int:pk>/', MappingDetailView.as_view(), name='mapping-detail'),
    path('patient/<int:patient_id>/', PatientAssignedDoctorsExplicitView.as_view(), name='patient-assigned-doctors'),
    path('remove/<int:patient_id>/<int:doctor_id>/', RemoveMappingExplicitView.as_view(), name='mapping-remove-explicit'),
]
