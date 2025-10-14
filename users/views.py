from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser, Restaurant, City, Address
from .serializers import CustomUserSerializer, CustomTokenObtainPairSerializer, RestaurantSerializer, CitySerializer, UserSerializer, UserLoginSerializer, AddressSerializer
import logging
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .views import *


logger = logging.getLogger(__name__)

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return Response({"detail": f"Failed to update user: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        logger.debug(f"Registration request data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = serializer.save()
            token = CustomTokenObtainPairSerializer.get_token(user)
            return Response({
                'user': UserSerializer(user).data,  # Use UserSerializer for full user data
                'access': str(token.access_token),
                'refresh': str(token),
            }, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            logger.error(f"IntegrityError during registration: {str(e)}")
            error_message = {"detail": "A user with this username or email already exists."}
            if "username" in str(e).lower():
                error_message["username"] = "This username is already taken."
            if "email" in str(e).lower():
                error_message["email"] = "This email is already registered."
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)


logger = logging.getLogger(__name__)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                user_data = UserSerializer(user, context={'request': request}).data
                logger.info(f"User {username} logged in successfully")
                logger.debug(f"User data in login response: {user_data}")
                if 'role' not in user_data:
                    logger.error(f"Role field missing in UserSerializer output for user {username}: {user_data}")
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': user_data
                }, status=status.HTTP_200_OK)
            logger.error(f"Invalid credentials for username: {username}")
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        logger.error(f"Login validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        logger.debug(f"Registration request data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = serializer.save()
            token = CustomTokenObtainPairSerializer.get_token(user)
            return Response({
                'user': UserSerializer(user).data,
                'access': str(token.access_token),
                'refresh': str(token),
            }, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            logger.error(f"IntegrityError during registration: {str(e)}")
            error_message = {"detail": "A user with this username or email already exists."}
            if "username" in str(e).lower():
                error_message["username"] = "This username is already taken."
            if "email" in str(e).lower():
                error_message["email"] = "This email is already registered."
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [AllowAny]

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching user profile: {str(e)}")
            return Response({"detail": "Failed to fetch user profile"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        try:
            serializer = UserSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            logger.error(f"Serializer validation failed: {serializer.errors}")
            return Response(
                {"detail": "Invalid data", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return Response({"detail": "Failed to update profile"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if serializer.validated_data.get('is_default'):
            Address.objects.filter(user=self.request.user, is_default=True).update(is_default=False)
        serializer.save(user=self.request.user)
        logger.info(f"Address created for user {self.request.user.username}: {serializer.validated_data}")

    def perform_update(self, serializer):
        if serializer.validated_data.get('is_default'):
            Address.objects.filter(user=self.request.user, is_default=True).exclude(id=self.get_object().id).update(is_default=False)
        serializer.save()
        logger.info(f"Address updated for user {self.request.user.username}: {serializer.validated_data}")

    def perform_destroy(self, instance):
        logger.info(f"Deleting address {instance.id} for user {self.request.user.username}")
        instance.delete()

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def contact_form_view(request):
    """
    Handle contact form submission and send email to admin
    """
    try:
        # Extract data
        first_name = request.data.get('firstName', '').strip()
        last_name = request.data.get('lastName', '').strip()
        email = request.data.get('email', '').strip()
        phone = request.data.get('phone', '').strip()
        subject = request.data.get('subject', 'No Subject')
        message = request.data.get('message', '').strip()

        # Basic validation
        if not email or not message:
            return Response({
                'detail': 'Email and message are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(message) < 10:
            return Response({
                'detail': 'Message must be at least 10 characters.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Format email content
        full_name = f"{first_name} {last_name}".strip() or "Anonymous"
        customer_subject = f"Contact Form: {subject}"
        email_body = f"""
        New contact form submission:

        Name: {full_name}
        Email: {email}
        Phone: {phone or 'Not provided'}
        Subject: {subject}

        Message:
        {message}

        ---
        This email was sent via Quicki Restaurant contact form.
        """

        # Send email
        send_mail(
            subject=customer_subject,
            message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.VAPID_ADMIN_EMAIL],  # Use your admin email
            fail_silently=False,
        )

        logger.info(f"Contact email sent successfully from {email}")
        return Response({
            'detail': 'Message sent successfully!'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Failed to send contact email: {str(e)}")
        return Response({
            'detail': 'Failed to send message. Please try again later.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)