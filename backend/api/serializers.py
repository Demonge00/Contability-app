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
    status = serializers.SerializerMethodField(read_only=True)
    product_picture = serializers.URLField(required=False)
    shop_delivery_cost = serializers.FloatField(required=False)
    shop_taxes = serializers.FloatField(required=False)
    own_taxes = serializers.FloatField(required=False)
    added_taxes = serializers.FloatField(required=False)
    total_cost = serializers.FloatField(required=True)

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
            "amount_buyed",
            "amount_delivered",
            "amount_received",
            "order",
            "status",
            "product_picture",
            "shop_cost",
            "shop_delivery_cost",
            "shop_taxes",
            "own_taxes",
            "added_taxes",
            "total_cost",
            "cost_per_product",
        ]
        read_only_fields = ["id"]

    def get_status(self, obj):
        count = 0
        try:
            for product in self.instance.filter(id=obj.id).first().buys.all():
                count += product.amount_buyed
        except AttributeError:
            if self.instance is None:
                return "Encargado"
            for product in self.instance.buys.all():
                count += product.amount_buyed
        if count == obj.amount_requested:
            return "Comprado"
        if count != 0:
            return "Parcialmente comprado"
        return "Encargado"

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
            "received_value_of_client",
            "extra_payments",
        ]
        depth = 0
        read_only_fields = ["id"]

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


class ProductBuyedSerializer(serializers.ModelSerializer):
    """Product buyed by the agent"""

    original_product = serializers.SlugRelatedField(
        queryset=Product.objects.all(),
        slug_field="id",
        error_messages={
            "does_not_exist": "El producto {value} no existe.",
            "invalid": "El valor proporcionado para el producto no es válido.",
        },
        write_only=True,
    )
    original_product_details = serializers.SerializerMethodField(read_only=True)
    order = serializers.SlugRelatedField(
        queryset=Order.objects.all(),
        slug_field="id",
        error_messages={
            "does_not_exist": "El pedido {value} no existe.",
            "invalid": "El valor proporcionado para el pedido no es válido.",
        },
    )
    shoping_receip = serializers.SlugRelatedField(
        queryset=ShoppingReceip.objects.all(),
        slug_field="id",
        error_messages={
            "does_not_exist": "El recibo de compra {value} no existe.",
            "invalid": "El valor proporcionado para el recibo no es válido.",
        },
    )

    class Meta:
        """Class of model"""

        model = ProductBuyed
        fields = [
            "id",
            "original_product",
            "order",
            "shoping_receip",
            "actual_cost_of_product",
            "amount_buyed",
            "shop_discount",
            "offer_discount",
            "buy_date",
            "observation",
            "real_cost_of_product",
            "original_product_details",
        ]
        read_only_fields = ["id"]

    def get_original_product_details(self, obj):
        return ProductSerializer(obj.original_product).data

    def validate(self, attrs):
        if attrs["amount_buyed"] <= 0:
            raise serializers.ValidationError(
                "La cantidad comprada debe ser un número positivo."
            )
        if (
            attrs["amount_buyed"] + attrs["original_product"].amount_buyed()
            > attrs["original_product"].amount_requested
        ):
            raise serializers.ValidationError(
                "La cantidad comprada no puede ser mayor a la solicitada."
            )
        return attrs


class ShoppingReceipSerializer(serializers.ModelSerializer):
    """Shopping Receip Serializer"""

    shopping_account = serializers.SlugRelatedField(
        queryset=BuyingAccounts.objects.all(),
        slug_field="account_name",
        error_messages={
            "does_not_exist": "La cuenta de compra {value} no existe.",
            "invalid": "El valor proporcionado para la cuenta de compra no es válido.",
        },
    )
    shop_of_buy = serializers.SlugRelatedField(
        queryset=Shop.objects.all(),
        slug_field="name",
        error_messages={
            "does_not_exist": "La tienda {value} no existe.",
            "invalid": "El valor proporcionado para la cuenta de compra no es válido.",
        },
    )
    buyed_products = ProductBuyedSerializer(many=True, read_only=True)

    class Meta:
        """Class of model"""

        model = ShoppingReceip
        fields = [
            "id",
            "shopping_account",
            "shop_of_buy",
            "total_cost_of_shopping",
            "buy_date",
            "buyed_products",
        ]
        read_only_fields = ["id"]


class ProductReceivedSerializer(serializers.ModelSerializer):
    """Product delivered and received by the logistical"""

    original_product = serializers.SlugRelatedField(
        queryset=Product.objects.all(),
        slug_field="id",
        error_messages={
            "does_not_exist": "El producto {value} no existe.",
            "invalid": "El valor proporcionado para el producto no es válido.",
        },
        write_only=True,
    )
    original_product_detail = serializers.SerializerMethodField(read_only=True)
    order = serializers.SlugRelatedField(
        queryset=Order.objects.all(),
        slug_field="id",
        error_messages={
            "does_not_exist": "El pedido {value} no existe.",
            "invalid": "El valor proporcionado para el pedido no es válido.",
        },
    )
    package_where_was_send = serializers.SlugRelatedField(
        queryset=Package.objects.all(),
        slug_field="id",
        error_messages={
            "does_not_exist": "El paquete {value} no existe.",
            "invalid": "El valor proporcionado para el paquete no es válido.",
        },
    )
    deliver_receip = serializers.SlugRelatedField(
        queryset=DeliverReceip.objects.all(),
        slug_field="id",
        error_messages={
            "does_not_exist": "El recibo de entrega {value} no existe.",
            "invalid": "El valor proporcionado para el recibo de entrega no es válido.",
        },
        required=False,
    )

    class Meta:
        model = ProductReceived
        fields = [
            "id",
            "original_product",
            "original_product_detail",
            "order",
            "reception_date_in_eeuu",
            "reception_date_in_cuba",
            "package_where_was_send",
            "deliver_receip",
            "amount_received",
            "amount_delivered",
            "observation",
        ]
        read_only_fields = ["id"]

    def get_original_product_detail(self, obj):
        return ProductSerializer(obj.original_product).data

    def validate(self, attrs):
        if attrs.get("amount_received") and attrs.get("original_product"):
            if attrs["amount_received"] <= 0:
                raise serializers.ValidationError(
                    "La cantidad recibida debe ser un número positivo."
                )
            if (
                attrs["original_product"].amount_requested
                < attrs["amount_received"] + attrs["original_product"].amount_received()
            ):
                raise serializers.ValidationError(
                    "La cantidad recibida no puede ser mayor a la solicitada."
                )
        if attrs.get("amount_delivered") and self.instance:
            print(self.instance.original_product)
            if attrs["amount_delivered"] <= 0:
                raise serializers.ValidationError(
                    f"La cantidad entregada debe ser un número positivo en el producto {self.instance.original_product.id}."
                )
            print(attrs["amount_delivered"])
            if (
                self.instance.amount_received
                < attrs["amount_delivered"]
                + self.instance.original_product.amount_delivered()
            ):
                raise serializers.ValidationError(
                    f"La cantidad entregada no puede ser mayor a la recibida en el producto {self.instance.original_product.id}."
                )
        return attrs


class DeliverReceipSerializer(serializers.ModelSerializer):
    """Deliver Receip Serializer"""

    order = serializers.SlugRelatedField(
        queryset=Order.objects.all(),
        slug_field="id",
        error_messages={
            "does_not_exist": "El pedido {value} no existe.",
            "invalid": "El valor proporcionado para el pedido no es válido.",
        },
    )
    deliver_picture = serializers.URLField(required=False)
    delivered_products = ProductReceivedSerializer(many=True, read_only=True)

    class Meta:
        model = DeliverReceip
        fields = [
            "id",
            "order",
            "deliver_date",
            "deliver_picture",
            "delivered_products",
            "weight",
            "status",
            "total_cost_of_deliver",
        ]
        read_only_fields = ["id"]


class PackageSerializer(serializers.ModelSerializer):
    """Package Serializer"""

    package_picture = serializers.URLField(required=False)
    contained_products = ProductReceivedSerializer(many=True, read_only=True)

    class Meta:
        model = Package
        fields = [
            "id",
            "number_of_tracking",
            "agency_name",
            "status_of_processing",
            "package_picture",
            "contained_products",
        ]
        read_only_fields = ["id"]
