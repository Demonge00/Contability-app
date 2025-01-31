"Vistas de la API"
import os
from rest_framework.fields import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from rest_framework import viewsets
from django.db import transaction
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.template import Context, Template
from django.core.mail import EmailMessage
from django.utils.crypto import get_random_string
from django.conf import settings
from api.permissions.permissions import (
    ReadOnly,
    ReadOnlyorPost,
    AccountantPermission,
    AdminPermission,
    AgentPermission,
    BuyerPermission,
    LogisticalPermission,
)
from api.serializers import (
    ShoppingReceipSerializer,
    UserSerializer,
    OrderSerializer,
    ShopSerializer,
    BuyingAccountsSerializer,
    CommonInformationSerializer,
    ProductSerializer,
    ProductBuyedSerializer,
    ProductReceivedSerializer,
    PackageSerializer,
    DeliverReceipSerializer,
)
from api.models import (
    Order,
    ProductBuyed,
    Shop,
    BuyingAccounts,
    CommonInformation,
    Product,
    ShoppingReceip,
    ProductReceived,
    Package,
    DeliverReceip,
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import cloudinary.uploader

User = get_user_model()


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
            subject = f"Verifica tu cuenta de usuario para {settings.WEB_SITE_NAME}"
            html_template_path = os.path.join(
                os.path.dirname(__file__), "utils", "email_html.html"
            )
            with open(html_template_path, "r", encoding="utf-8") as file:
                html_template_content = file.read()
            template = Template(html_template_content)
            context = Context(
                {
                    "user_name": self.request.data["name"],
                    "verification_url": f"{settings.VERIFICATION_URL}{verify_secret}",
                }
            )
            html_message = template.render(context)
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [self.request.data["email"]]
            email = EmailMessage(subject, html_message, from_email, recipient_list)
            email.content_subtype = "html"  # Configurar el contenido como HTML
            email.send()
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
    lookup_field = "name"

    def get_object(self):
        try:
            shop = Shop.objects.get(name=self.kwargs["name"])
        except Exception as e:
            raise ValidationError({"error": str(e)}) from e
        return shop


class BuyingAccountsViewsSet(viewsets.ModelViewSet):
    queryset = BuyingAccounts.objects.all()
    serializer_class = BuyingAccountsSerializer
    permission_classes = [ReadOnly | AdminPermission]


class CommonInformationViewSet(viewsets.ModelViewSet):
    queryset = CommonInformation.objects.all()
    serializer_class = CommonInformationSerializer
    permission_classes = [ReadOnly | AdminPermission]

    def get_object(self):
        return CommonInformation.objects.first()


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [ReadOnly | AgentPermission]

    def create(self, request, *args, **kwargs):
        product_picture = None
        if "product_picture" in self.request.FILES:
            picture = self.request.FILES.get("product_picture")
            if not picture.name.lower().endswith((".png", ".jpg", ".jpeg")):
                raise ValidationError(
                    "El archivo debe ser una imagen (.png, .jpg, .jpeg)."
                )
            try:
                upload_result = cloudinary.uploader.upload(picture, quality=10)
            except Exception as e:
                raise ValidationError(str(e)) from e
            product_picture = upload_result["secure_url"]
        if product_picture is not None:
            request.data["product_picture"] = product_picture
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        product_picture = None
        if "product_picture" in self.request.FILES:
            picture = self.request.FILES.get("product_picture")
            if not picture.name.lower().endswith((".png", ".jpg", ".jpeg")):
                raise ValidationError(
                    "El archivo debe ser una imagen (.png, .jpg, .jpeg)."
                )
            try:
                upload_result = cloudinary.uploader.upload(picture, quality=10)
            except Exception as e:
                raise ValidationError(str(e)) from e
            product_picture = upload_result["secure_url"]
        request.data["product_picture"] = product_picture
        return super().update(request, *args, **kwargs)


class ShoppingReceipViewSet(viewsets.ModelViewSet):
    queryset = ShoppingReceip.objects.all()
    serializer_class = ShoppingReceipSerializer
    permission_classes = [ReadOnly | BuyerPermission]

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            if "shopping_account" in request.data and "shop_of_buy" in request.data:
                serializer = ShoppingReceipSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                try:
                    if "buyed_products" in request.data:
                        for product in request.data["buyed_products"]:
                            product["shoping_receip"] = serializer.data["id"]
                            product_serializer = ProductBuyedSerializer(data=product)
                            product_serializer.is_valid(raise_exception=True)
                            product_serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    raise ValidationError(
                        f"Error al procesar productos: {str(e)}"
                    ) from e
            return Response(
                {"message": "Faltan datos"}, status=status.HTTP_400_BAD_REQUEST
            )


class ProductBuyedViewSet(viewsets.ModelViewSet):
    queryset = ProductBuyed.objects.all()
    serializer_class = ProductBuyedSerializer
    permission_classes = [ReadOnly | AccountantPermission]


class ProductReceivedViewSet(viewsets.ModelViewSet):
    queryset = ProductReceived.objects.all()
    serializer_class = ProductReceivedSerializer
    permission_classes = [ReadOnly | LogisticalPermission]

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                if "contained_products" in request.data and (
                    "package_where_was_send" in request.data
                ):
                    contained_products = request.data["contained_products"]
                    for product in contained_products:
                        product["package_where_was_send"] = request.data[
                            "package_where_was_send"
                        ]
                        product_serializer = ProductReceivedSerializer(data=product)
                        product_serializer.is_valid(raise_exception=True)
                        product_serializer.save()
                return Response(
                    {"Message": "Product Creation success"},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                raise ValidationError(f"Error al procesar productos: {str(e)}") from e

    @action(detail=False, methods=["patch"], permission_classes=[IsAuthenticated])
    def deliver_products(self, request):
        with transaction.atomic():
            try:
                if "delivered_products" in request.data and (
                    "deliver_receip" in request.data
                    and not "package_where_was_send" in request.data
                ):
                    delivered_products = request.data["delivered_products"]
                    for product in delivered_products:

                        instance = ProductReceived.objects.get(id=product["id"])
                        product["deliver_receip"] = request.data["deliver_receip"]
                        product_serializer = ProductReceivedSerializer(
                            instance, data=product, partial=True
                        )
                        product_serializer.is_valid(raise_exception=True)
                        product_serializer.save()
                        print(product_serializer.data)
                    return Response(
                        {"Message": "Product Creation success"},
                        status=status.HTTP_201_CREATED,
                    )
                raise ValidationError("Argumentos incompletos o incorrectos")
            except Exception as e:
                raise ValidationError(f"Error al procesar productos: {str(e)}") from e


class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [ReadOnly | LogisticalPermission]

    def create(self, request, *args, **kwargs):
        package_picture = None
        if "package_picture" in request.FILES:
            picture = self.request.FILES.get("package_picture")
            if not picture.name.lower().endswith((".png", ".jpg", ".jpeg")):
                raise ValidationError(
                    "El archivo debe ser una imagen (.png, .jpg, .jpeg)."
                )
            try:
                upload_result = cloudinary.uploader.upload(picture, quality=10)
                package_picture = upload_result["secure_url"]
            except Exception as e:
                raise ValidationError(str(e)) from e
        if package_picture:
            request.data["package_picture"] = package_picture
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        package_picture = None
        if "package_picture" in request.FILES:
            picture = self.request.FILES.get("package_picture")
            if not picture.name.lower().endswith((".png", ".jpg", ".jpeg")):
                raise ValidationError(
                    "El archivo debe ser una imagen (.png, .jpg, .jpeg)."
                )
            try:
                upload_result = cloudinary.uploader.upload(picture, quality=10)
                package_picture = upload_result["secure_url"]
            except Exception as e:
                raise ValidationError(str(e)) from e
        if package_picture:
            request.data["package_picture"] = package_picture
        return super().create(request, *args, **kwargs)


class DeliverReceipViewSet(viewsets.ModelViewSet):
    queryset = DeliverReceip.objects.all()
    serializer_class = DeliverReceipSerializer
    permission_classes = [ReadOnly | LogisticalPermission]

    def create(self, request, *args, **kwargs):
        deliver_picture = None
        if "deliver_picture" in request.FILES:
            picture = self.request.FILES.get("deliver_picture")
            if not picture.name.lower().endswith((".png", ".jpg", ".jpeg")):
                raise ValidationError(
                    "El archivo debe ser una imagen (.png, .jpg, .jpeg)."
                )
            try:
                upload_result = cloudinary.uploader.upload(picture, quality=10)
                deliver_picture = upload_result["secure_url"]
            except Exception as e:
                raise ValidationError(str(e)) from e
        if deliver_picture:
            request.data["deliver_picture"] = deliver_picture
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        deliver_picture = None
        if "deliver_picture" in request.FILES:
            picture = self.request.FILES.get("deliver_picture")
            if not picture.name.lower().endswith((".png", ".jpg", ".jpeg")):
                raise ValidationError(
                    "El archivo debe ser una imagen (.png, .jpg, .jpeg)."
                )
            try:
                upload_result = cloudinary.uploader.upload(picture, quality=10)
                deliver_picture = upload_result["secure_url"]
            except Exception as e:
                raise ValidationError(str(e)) from e
        if deliver_picture:
            request.data["deliver_picture"] = deliver_picture
        return super().update(request, *args, **kwargs)
