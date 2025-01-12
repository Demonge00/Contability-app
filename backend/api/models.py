"""Models for api app"""

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from api.managers import CustomUserManager

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
        return str(self.email)

    def verify(self):
        """Verify user account"""
        self.is_verified = True
        self.is_active = True
        self.save()
