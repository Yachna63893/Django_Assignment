from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        style={'input_type': 'password'},
        help_text="Password must be at least 6 characters long."
    )

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password')
        extra_kwargs = {
            'name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
        }

    def validate_email(self, value):
        normalized_email = value.lower().strip()
        if User.objects.filter(email=normalized_email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized_email

    def validate_name(self, value):
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError("Name cannot be empty.")
        return trimmed

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        email = attrs.get('email', '').lower().strip()
        password = attrs.get('password', '')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        refresh = RefreshToken.for_user(user)

        return {
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'date_joined')
        read_only_fields = ('id', 'date_joined')
