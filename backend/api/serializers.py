from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from api.models import (
    CommonInformation,
    CustomUser,
    Shop,
    BuyingAccounts,
    ShoppingReceip,
    Product,
    DeliverReceip,
    Package,
    ProductBuyed,
    ProductReceived,
    Order,
)
import re


class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="id", read_only=True)
    email = serializers.EmailField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    is_agent = serializers.BooleanField(required=False)
    is_accountant = serializers.BooleanField(required=False)
    is_buyer = serializers.BooleanField(required=False)
    is_logistical = serializers.BooleanField(required=False)
    is_comunity_manager = serializers.BooleanField(required=False)
    is_staff = serializers.BooleanField(required=False)
    agent_profit = serializers.FloatField(required=False)

    class Meta:
        """Class of model"""

        model = CustomUser
        fields = [
            "user_id",
            "email",
            "name",
            "password",
            "last_name",
            "home_address",
            "phone_number",
            "is_agent",
            "is_accountant",
            "is_buyer",
            "is_logistical",
            "is_comunity_manager",
            "agent_profit",
            "is_staff",
        ]

    def validate_email(self, value):
        """Verification of email"""
        if value:
            if CustomUser.objects.filter(email=value).exists():
                raise serializers.ValidationError({"error": "El email ya existe."})
        return value

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class ProductSerializer(serializers.ModelSerializer):
    """Product information provided by the agent"""

    shop = serializers.SlugRelatedField(
        queryset=Shop.objects.all(),
        slug_field="name",
        error_messages={
            "does_not_exist": "La tienda {value} no existe.",
            "invalid": "El valor proporcionado para la tienda no es válido.",
        },
    )
    order = serializers.SlugRelatedField(
        queryset=Order.objects.all(),
        slug_field="id",
        error_messages={
            "does_not_exist": "El pedido {value} no existe.",
            "invalid": "El valor proporcionado para el pedido no es válido.",
        },
    )
    link = serializers.URLField(required=False)
    description = serializers.CharField(required=False, max_length=100)
    observation = serializers.CharField(required=False, max_length=100)
    category = serializers.CharField(required=False, max_length=100)
    status = serializers.CharField(required=False, max_length=100)
    product_picture = serializers.URLField(required=False)
    shop_delivery_cost = serializers.FloatField(required=False)
    shop_taxes = serializers.FloatField(required=False)
    own_taxes = serializers.FloatField(required=False)
    added_taxes = serializers.FloatField(required=False)

    class Meta:
        """MetaClassName"""

        model = Product
        fields = [
            "id",
            "sku",
            "name",
            "link",
            "shop",
            "description",
            "observation",
            "category",
            "amount_requested",
            "order",
            "status",
            "product_picture",
            "shop_cost",
            "shop_delivery_cost",
            "shop_taxes",
            "own_taxes",
            "added_taxes",
            "total_cost",
        ]
        read_only_fields = ["id"]

    def validate_shop_cost(self, value):
        """Ensure shop_cost is not negative."""
        if value < 0:
            raise serializers.ValidationError(
                "El costo de la tienda no puede ser negativo."
            )
        return value

    def validate_amount_requested(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "La cantidad solicitada debe ser un número positivo."
            )
        return value

    def validate_total_cost(self, value):
        """Ensure shop_cost is not negative."""
        if value < 0:
            raise serializers.ValidationError(
                "El costo de la tienda no puede ser negativo."
            )
        return value


class OrderSerializer(serializers.ModelSerializer):
    client = serializers.SlugRelatedField(
        queryset=CustomUser.objects.all(),
        slug_field="email",
        error_messages={
            "does_not_exist": "El cliente con el correo {value} no existe.",
            "invalid": "El valor proporcionado para el cliente no es válido.",
        },
    )
    sales_manager = serializers.SlugRelatedField(
        slug_field="email",
        read_only=True,
        error_messages={
            "does_not_exist": "El agente con el correo {value} no existe.",
            "invalid": "El valor proporcionado para el agente no es válido.",
        },
    )
    status = serializers.CharField(max_length=100, required=False, default="Encargado")
    pay_status = serializers.CharField(max_length=100, required=False)
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        """Class of model"""

        model = Order
        fields = [
            "id",
            "client",
            "sales_manager",
            "status",
            "pay_status",
            "total_cost",
            "products",
            "received_products",
            "received_value_of_client",
            "extra_payments",
        ]
        depth = 2

    def update(self, instance, validated_data):
        # Verificar si el campo 'client' está siendo modificado
        if "sales_manager" in validated_data:
            if instance.sales_manager != validated_data["sales_manager"]:
                raise serializers.ValidationError(
                    {"client": "No se puede cambiar el agente después de la creación."}
                )

        # Proceder con la actualización normal
        return super().update(instance, validated_data)

    def validate_sales_manager(self, value):
        """Agent Validation"""
        if CustomUser.objects.get(email=value.email).is_agent:
            return value
        raise serializers.ValidationError("El usuario no es agente.")


class ShopSerializer(serializers.ModelSerializer):
    """Serializer of diferents shops"""

    name = serializers.CharField(max_length=100)
    link = serializers.URLField()

    class Meta:
        """Class of model"""

        model = Shop
        fields = ["name", "link"]


class BuyingAccountsSerializer(serializers.ModelSerializer):
    """Serializer of buying accounts"""

    account_name = serializers.CharField(max_length=100)

    class Meta:
        """Class of model"""

        model = BuyingAccounts
        fields = ["account_name"]


class CommonInformationSerializer(serializers.ModelSerializer):
    """Common information introduced for the admin"""

    change_rate = serializers.FloatField()
    cost_per_pound = serializers.FloatField()

    class Meta:
        """Class of model"""

        model = CommonInformation
        fields = ["change_rate", "cost_per_pound"]


class ShoppingReceipSerializer(serializers.ModelSerializer):
    """Common information introduced for the admin"""

    change_rate = serializers.FloatField(required=False)
    cost_per_pound = serializers.FloatField(required=False)

    class Meta:
        """Class of model"""

        model = ShoppingReceip
