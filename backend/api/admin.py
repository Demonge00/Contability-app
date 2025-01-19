"""Admin page"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Order


class CustomUserAdmin(UserAdmin):
    """Admin Class for User"""

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = (
        "name",
        "email",
        "id",
        "is_active",
        "is_verified",
        "is_agent",
        "is_accountant",
        "is_buyer",
        "is_logistical",
        "is_comunity_manager",
        "agent_profit",
    )
    list_filter = (
        "name",
        "email",
        "id",
        "is_active",
        "is_verified",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "email",
                    "password",
                    "home_address",
                    "phone_number",
                    "is_agent",
                    "is_accountant",
                    "is_buyer",
                    "is_logistical",
                    "is_comunity_manager",
                    "agent_profit",
                )
            },
        ),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Order)
