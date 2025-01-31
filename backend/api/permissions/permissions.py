"Vistas de la API"
from rest_framework.fields import ValidationError
from rest_framework import permissions
from rest_framework.permissions import BasePermission
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

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

    def has_permission(self, request, view):
        try:
            user = User.objects.get(id=request.user.id)
            return user.is_agent
        except Exception as e:
            raise ValidationError("El usuario no es un agente") from e

    def has_object_permission(self, request, view, obj):
        try:
            user = User.objects.get(id=request.user.id)
            return user.is_agent
        except Exception as e:
            raise ValidationError("El usuario no es un agente") from e


class AccountantPermission(BasePermission):
    """Clase de permisos de agente"""

    def has_permission(self, request, view):
        try:
            user = User.objects.get(id=request.user.id)
            return user.is_accountant
        except Exception as e:
            raise ValidationError("El usuario no es un contador") from e

    def has_object_permission(self, request, view, obj):
        try:
            user = User.objects.get(id=request.user.id)
            return user.is_accountant
        except Exception as e:
            raise ValidationError("El usuario no es un contador") from e


class BuyerPermission(BasePermission):
    """Clase de permisos de agente"""

    def has_permission(self, request, view):
        try:
            user = User.objects.get(id=request.user.id)
            return user.is_buyer
        except Exception as e:
            raise ValidationError("El usuario no es un comprador") from e

    def has_object_permission(self, request, view, obj):
        try:
            user = User.objects.get(id=request.user.id)
            return user.is_buyer
        except Exception as e:
            raise ValidationError("El usuario no es un comprador") from e


class LogisticalPermission(BasePermission):
    """Clase de permisos de agente"""

    def has_permission(self, request, view):
        try:
            user = User.objects.get(id=request.user.id)
            return user.is_logistical
        except Exception as e:
            raise ValidationError("El usuario no es un comprador") from e

    def has_object_permission(self, request, view, obj):
        try:
            user = User.objects.get(id=request.user.id)
            return user.is_logistical
        except Exception as e:
            raise ValidationError("El usuario no es un comprador") from e


class AdminPermission(BasePermission):
    """Clase de permisos de agente"""

    def has_permission(self, request, view):
        try:
            user = User.objects.get(id=request.user.id)
            return user.is_staff
        except Exception as e:
            raise ValidationError("El usuario no es un administrador") from e

    def has_object_permission(self, request, view, obj):
        try:
            user = User.objects.get(id=request.user.id)
            return user.is_staff
        except Exception as e:
            raise ValidationError("El usuario no es un administrador") from e
