"""
URL configuration for healthcare_project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from drf_spectacular.utils import extend_schema


@extend_schema(
    summary="API Discovery Root",
    description="Directory overview of all endpoints and services in the Healthcare system."
)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Healthcare Backend API Root
    Overview of all available endpoints in the system.
    """
    return Response({
        'system': 'Healthcare Management Backend API',
        'version': '1.0.0',
        'documentation': {
            'swagger_ui': '/api/docs/',
            'redoc': '/api/redoc/',
            'openapi_schema': '/api/schema/'
        },
        'authentication': {
            'register': '/api/auth/register/',
            'login': '/api/auth/login/',
            'token_refresh': '/api/auth/token/refresh/',
            'profile': '/api/auth/profile/'
        },
        'patients': {
            'list_create': '/api/patients/',
            'detail_update_delete': '/api/patients/<id>/'
        },
        'doctors': {
            'list_create': '/api/doctors/',
            'detail_update_delete': '/api/doctors/<id>/'
        },
        'mappings': {
            'list_create': '/api/mappings/',
            'get_patient_doctors_or_detail': '/api/mappings/<patient_id>/',
            'delete_mapping': '/api/mappings/<id>/',
            'explicit_patient_doctors': '/api/mappings/patient/<patient_id>/',
            'explicit_remove': '/api/mappings/remove/<patient_id>/<doctor_id>/'
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),

    # Interactive Documentation & Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API Root
    path('', api_root, name='root'),
    path('api/', api_root, name='api-root'),

    # Core Application APIs
    path('api/auth/', include('authentication.urls')),
    path('api/patients/', include('patients.urls')),
    path('api/doctors/', include('doctors.urls')),
    path('api/mappings/', include('mappings.urls')),
]
