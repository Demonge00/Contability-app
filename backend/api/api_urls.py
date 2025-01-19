"""Api Urls"""

from django.urls import include, path, re_path
from api import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r"user", views.UserViewSet)
router.register(r"order", views.OrderViewSet)
router.register(r"shop", views.ShopViewSet)
router.register(r"buying_account", views.BuyingAccountsViewsSet)
router.register(r"common_information", views.CommonInformationViewSet)
router.register(r"product", views.ProductViewSet)
urlpatterns = [
    path("", include(router.urls)),
    path("verify_user/<verification_secret>", views.verify_user, name="verify_user"),
    path("token/", views.MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    re_path(
        "password/(?P<password_secret>\S+)?/?$",
        views.PasswordRecoverList.as_view(),
        name="recover_password",
    ),
    path("security/", views.Protection.as_view(), name="posting_management"),
]
