"""Models for api app"""

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from api.managers import CustomUserManager
import uuid

# Create your models here.


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom user model"""

    # Account data
    email = models.EmailField(_("email address"), unique=True)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    home_address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    is_agent = models.BooleanField(default=False)
    is_accountant = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=False)
    is_logistical = models.BooleanField(default=False)
    is_comunity_manager = models.BooleanField(default=False)
    agent_profit = models.FloatField(default=0)

    # Account management
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    sent_verification_email = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_secret = models.CharField(max_length=200, blank=True, null=True)
    password_secret = models.CharField(max_length=200, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.name + " " + self.last_name

    def verify(self):
        """Verify user account"""
        self.is_verified = True
        self.is_active = True
        self.save()


class Order(models.Model):
    """Orders in shops"""

    client = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="orders"
    )
    sales_manager = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="managed_orders"
    )
    status = models.CharField(max_length=100)
    pay_status = models.CharField(max_length=100, default="No pagado")

    def __str__(self):
        return "Pedido #" + str(self.pk) + " creado por " + str(self.client.name)

    def total_cost(self):
        """Total cost of order"""
        cost = 0
        if self.products.all():
            for i in self.products.all():
                cost += i.shop_cost
        return cost

    def received_products(self):
        """Total products reciebed"""
        prodlist = []
        if self.delivery_receipts.all():
            for i in self.delivery_receipts.all():
                prodlist.insert(-1, i)
        return prodlist

    def received_value_of_client(self):
        """Total value of objects receives by client"""
        value = 0
        if self.delivery_receipts.all():
            for i in self.delivery_receipts.all():
                value += i.total_cost_of_deliver()
        return value

    def extra_payments(self):
        """Extra payment in case of excedent or missing"""
        return self.received_value_of_client() - self.total_cost()

    objects = models.Manager()


class Shop(models.Model):
    """Shops in catalog"""

    name = models.CharField(max_length=100, unique=True)
    link = models.URLField(unique=True)

    objects = models.Manager()


class BuyingAccounts(models.Model):
    """Accounts for buying in Shops"""

    account_name = models.CharField(max_length=100, unique=True)

    objects = models.Manager()


class CommonInformation(models.Model):
    """Common information introduced for the admin"""

    change_rate = models.FloatField(default=0)
    cost_per_pound = models.FloatField(default=0)

    objects = (
        models.Manager()
    )  # Add this line to ensure the objects manager is available


class Product(models.Model):
    """Products in shop"""

    # Product information
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )
    sku = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    link = models.URLField(blank=True, null=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    description = models.TextField(max_length=200, null=True)
    observation = models.TextField(max_length=200, null=True)
    category = models.CharField(max_length=200, null=True)
    amount_requested = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="products")
    status = models.CharField(max_length=100, default="Encargado")
    product_picture = models.URLField(blank=True, null=True)

    # Product prices
    shop_cost = models.FloatField()
    shop_delivery_cost = models.FloatField(default=0)
    shop_taxes = models.FloatField(default=0)
    own_taxes = models.FloatField(default=0)
    added_taxes = models.FloatField(default=0)
    total_cost = models.FloatField(default=0)

    # def total_cost(self):
    #     """Total cost of product"""
    #     return (
    #         self.shop_cost
    #         * self.shop_delivery_cost
    #         * self.shop_taxes
    #         * self.own_taxes
    #         * self.added_taxes
    #     )

    objects = models.Manager()

    def cost_per_product(self):
        """Cost after payment for product"""
        cost = 0
        ocurrences = 0
        for i in self.buys.all():
            cost += i.actual_cost_of_product
            ocurrences += i.amount_buyed
        return float(cost / ocurrences)


class ShoppingReceip(models.Model):
    """Receip for each buy in shops"""

    shopping_account = models.ForeignKey(
        BuyingAccounts, on_delete=models.CASCADE, related_name="buys"
    )
    shop_of_buy = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="buys")
    status_of_shopping = models.CharField(max_length=100)

    objects = models.Manager()

    def total_cost_of_shopping(self):
        cost = 0
        for i in self.buyed_products.all():
            cost += i.real_cost_of_product()
        return cost


class DeliverReceip(models.Model):
    """Receip given periodicaly to user every time they get products"""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="delivery_receipts"
    )
    weight = models.FloatField()
    status = models.CharField(max_length=100)
    deliver_picture = models.URLField()

    objects = models.Manager()

    def total_cost_of_deliver(self):
        """Total cost of delivered objects"""
        cost = self.weight * CommonInformation.objects.get(pk=1).cost_per_pound
        for i in self.delivered_products.all():
            cost += i.original_product.cost_per_product() * i.amount_received
        return cost


class Package(models.Model):
    """Packages sent with products"""

    agency_name = models.CharField(max_length=100)
    number_of_tracking = models.CharField(max_length=100)
    status_of_processing = models.CharField(max_length=100)
    package_picture = models.URLField()

    objects = models.Manager()


class ProductBuyed(models.Model):
    """Buyed Products"""

    original_product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="buys"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="buyed_products"
    )
    actual_cost_of_product = models.FloatField(null=True, blank=True)
    shop_discount = models.FloatField(default=0)
    offer_discount = models.FloatField(default=0)
    buy_date = models.DateField(default=timezone.now)
    shoping_receip = models.ForeignKey(
        ShoppingReceip, on_delete=models.CASCADE, related_name="buyed_products"
    )
    amount_buyed = models.IntegerField()
    observation = models.TextField(max_length=200, null=True)
    real_cost_of_product = models.FloatField()

    objects = models.Manager()

    # def real_cost_of_product(self):
    #     return (
    #         self.original_product.total_cost()
    #         * self.shop_discount
    #         * self.offer_discount
    #     )


class ProductReceived(models.Model):
    """Buyed Products"""

    original_product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="delivers"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="recieved_products"
    )
    reception_date_in_eeuu = models.DateField(default=timezone.now)
    reception_date_in_cuba = models.DateField(null=True, blank=True)
    package_where_was_send = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name="contained_products"
    )
    deliver_receip = models.ForeignKey(
        DeliverReceip, on_delete=models.CASCADE, related_name="delivered_products"
    )
    amount_received = models.IntegerField()
    observation = models.TextField(max_length=200, null=True)

    objects = models.Manager()
