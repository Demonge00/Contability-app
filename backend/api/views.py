"Vistas de la API"
from rest_framework.fields import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from api.serializers import (
    UserSerializer,
    OrderSerializer,
    ShopSerializer,
    BuyingAccountsSerializer,
    CommonInformationSerializer,
    ProductSerializer,
)
from api.models import Order, Shop, BuyingAccounts, CommonInformation, Product
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import cloudinary.uploader

User = get_user_model()


class ReadOnlyorPost(BasePermission):
    "Clase de permisos para crear"

    def has_permission(self, request, view):
        return request.method in ["GET", "POST"]


class ReadOnly(BasePermission):
    "Clase de permisos para crear"

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class AgentPermission(BasePermission):
    """Clase de permisos de agente"""

    def has_object_permission(self, request, view, obj):
        user = User.objects.get(id=request.user.id)
        return user.is_agent


class AdminPermission(BasePermission):
    """Clase de permisos de agente"""

    def has_object_permission(self, request, view, obj):
        user = User.objects.get(id=request.user.id)
        return user.is_staff


# Auth JWt


class MyTokenObtainPairView(TokenObtainPairView):
    "Vista del serializer"
    serializer_class = TokenObtainPairSerializer


class Protection(APIView):
    """
    Seguridad contra ausencia de token
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Respuesta de seguridad"""
        if request:
            return Response(status=status.HTTP_200_OK)
        raise ValidationError({"message": "no_request"})


# UserManagement


class UserViewSet(viewsets.ModelViewSet):
    "Vista de usuario"

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated | ReadOnlyorPost]

    def perform_create(self, serializer):
        verify_secret = get_random_string(length=32)
        try:
            send_mail(
                f"Verifica tu cuenta de usuario para {settings.WEB_SITE_NAME}",
                f"Para verificar tu cuenta en {settings.WEB_SITE_NAME}, ve a {settings.VERIFICATION_URL}{verify_secret}",
                settings.SENDER_EMAIL,
                [self.request.data["email"]],
                fail_silently=False,
                html_message=f'Porfavor ve a <a href="{settings.VERIFICATION_URL}{verify_secret}">este email</a> para verificar tu cuenta.',
            )
        except Exception as e:
            raise ValidationError({"error": str(e)}) from e
        return serializer.save(
            verification_secret=verify_secret,
            sent_verification_email=True,
        )


class PasswordRecoverList(APIView):
    "Vista de recuperacion de contraseña"

    def post(self, request):
        "Sender email password"
        password_secret = get_random_string(length=32)
        try:
            user = User.objects.get(email=request.data["email"])
            user.password_secret = password_secret
            user.save()
            print(
                f"Porfavor ve a <a href='http://localhost:5173/recover-password/{password_secret}'>este link</a> para vambiar tu contraseña."
            )
            return Response(
                {"message": "Password recuperado"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            raise ValidationError({"message": "Email no existe" + e}) from e

    def put(self, request, password_secret=None):
        """Update password"""
        try:
            user = User.objects.get(password_secret=password_secret)
            user.set_user_password(request.data["password"])
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError({"message": "Error"}) from e


@api_view(["GET"])
def verify_user(request, verification_secret):
    """Verificate user email"""
    if request:
        try:
            user = User.objects.get(verification_secret=verification_secret)
            user.verify()
            return Response({"message": "user_registered"}, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError({"message": "unable to register user"}) from e
    raise ValidationError({"message": "no_request"})


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AgentPermission & (IsAuthenticated | ReadOnlyorPost)]

    def perform_create(self, serializer):
        user = User.objects.get(id=self.request.user.id)
        return serializer.save(sales_manager=user)

    # @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])


class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [ReadOnly | AdminPermission]


class BuyingAccountsViewsSet(viewsets.ModelViewSet):
    queryset = BuyingAccounts.objects.all()
    serializer_class = BuyingAccountsSerializer
    permission_classes = [ReadOnly | AdminPermission]


class CommonInformationViewSet(viewsets.ModelViewSet):
    queryset = CommonInformation.objects.all()
    serializer_class = CommonInformationSerializer
    permission_classes = [ReadOnly | AdminPermission]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [ReadOnly | AgentPermission]
