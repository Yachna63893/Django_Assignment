from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Registers a new user with name, email, and password.
    Returns user details along with JWT access and refresh tokens.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens for immediate access
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'success': True,
                'message': 'User registered successfully.',
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    """
    POST /api/auth/login/
    Logs in an existing user and returns JWT access and refresh tokens.
    """
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    @extend_schema(
        summary="User Login",
        description="Authenticates a user with email and password, returning JWT access and refresh tokens.",
        request=UserLoginSerializer,
        responses={200: OpenApiResponse(description="Login successful with tokens and user details.")}
    )
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        return Response(
            {
                'success': True,
                'message': 'Login successful.',
                'user': validated_data['user'],
                'tokens': validated_data['tokens'],
                # Top level token fields for convenience across different API clients
                'access': validated_data['tokens']['access'],
                'refresh': validated_data['tokens']['refresh']
            },
            status=status.HTTP_200_OK
        )


class ProfileView(generics.RetrieveAPIView):
    """
    GET /api/auth/profile/
    Returns the current authenticated user's profile.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
