import django_filters
from django.db.models import Avg, Count, Min, Sum

from api.models import (
    CustomUser,
    DeliverReceip,
    Order,
    Package,
    Product,
    ProductBuyed,
    ProductReceived,
    ShoppingReceip,
)


class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    home_address = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = CustomUser
        fields = ["name", "email", "last_name", "is_agent", "home_address"]


class OrderFilter(django_filters.FilterSet):

    client = django_filters.CharFilter(
        field_name="client", lookup_expr="name__icontains"
    )
    sales_manager = django_filters.CharFilter(
        field_name="sales_manager", lookup_expr="name__icontains"
    )
    min_cost = django_filters.NumberFilter(
        method="filter_total_cost_gte",
    )
    max_cost = django_filters.NumberFilter(
        method="filter_total_cost_lte",
    )
    initial_date = django_filters.DateFilter(
        field_name="creation_date", lookup_expr="date__gte"
    )
    final_date = django_filters.DateFilter(
        field_name="creation_date", lookup_expr="date__lte"
    )

    class Meta:
        model = Order
        fields = ["status"]

    def filter_total_cost_gte(self, queryset, name, value):
        # Annotate the queryset with total_cost
        queryset = queryset.annotate(sum_of_cost=Sum("products__total_cost", default=0))

        return queryset.filter(sum_of_cost__gte=value)

    def filter_total_cost_lte(self, queryset, name, value):
        # Annotate the queryset with total_cost
        queryset = queryset.annotate(sum_of_cost=Sum("products__total_cost", default=0))

        return queryset.filter(sum_of_cost__lte=value)


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    category = django_filters.CharFilter(lookup_expr="icontains")
    order = django_filters.NumberFilter(field_name="order", lookup_expr="id__exact")
    client_id = django_filters.CharFilter(
        field_name="order", lookup_expr="client__id__exact"
    )
    min_cost = django_filters.NumberFilter(field_name="shop_cost", lookup_expr="gte")
    max_cost = django_filters.NumberFilter(field_name="shop_cost", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["sku", "shop__name", "category", "status", "name"]


class DeliverReceipFilter(django_filters.FilterSet):
    order = django_filters.NumberFilter(field_name="order", lookup_expr="id__exact")
    client = django_filters.CharFilter(
        field_name="order", lookup_expr="client__id__exact"
    )
    deliver_date = django_filters.DateFilter(
        field_name="deliver_date", lookup_expr="date"
    )
    initial_date = django_filters.DateFilter(
        field_name="deliver_date", lookup_expr="date__gte"
    )
    final_date = django_filters.DateFilter(
        field_name="deliver_date", lookup_expr="date__lte"
    )
    min_weight = django_filters.NumberFilter(field_name="weight", lookup_expr="gte")
    max_weight = django_filters.NumberFilter(field_name="weight", lookup_expr="lte")

    class Meta:
        model = DeliverReceip
        fields = ["status"]


class ShoppingReceipFilter(django_filters.FilterSet):
    shopping_account = django_filters.CharFilter(
        field_name="shopping_account", lookup_expr="account_name__icontains"
    )
    shop__name = django_filters.CharFilter(
        field_name="shop_of_buy", lookup_expr="name__icontains"
    )
    state = django_filters.CharFilter(
        field_name="status_of_shopping", lookup_expr="state__icontains"
    )
    buy_date = django_filters.DateFilter(field_name="buy_date", lookup_expr="date")
    initial_date = django_filters.DateFilter(
        field_name="buy_date", lookup_expr="date__gte"
    )
    final_date = django_filters.DateFilter(
        field_name="buy_date", lookup_expr="date__lte"
    )
    min_cost = django_filters.NumberFilter(
        method="filter_total_cost_gte",
    )
    max_cost = django_filters.NumberFilter(
        method="filter_total_cost_lte",
    )
    buyed_products = django_filters.ModelMultipleChoiceFilter(
        field_name="buyed_products",
        to_field_name="id",
        queryset=ProductBuyed.objects.all(),
    )

    class Meta:
        model = ShoppingReceip
        fields = ["status_of_shopping"]

    def filter_total_cost_gte(self, queryset, name, value):
        # Annotate the queryset with total_cost
        queryset = queryset.annotate(
            sum_of_cost=Sum("buyed_products__real_cost_of_product", default=0)
        )

        return queryset.filter(sum_of_cost__gte=value)

    def filter_total_cost_lte(self, queryset, name, value):
        # Annotate the queryset with total_cost
        queryset = queryset.annotate(
            sum_of_cost=Sum("buyed_products__real_cost_of_product", default=0)
        )

        return queryset.filter(sum_of_cost__lte=value)


class PackageFilter(django_filters.FilterSet):
    agency_name = django_filters.CharFilter(lookup_expr="icontains")
    contained_products = django_filters.ModelMultipleChoiceFilter(
        field_name="contained_products",
        to_field_name="id",
        queryset=ProductReceived.objects.all(),
    )

    class Meta:
        model = Package
        fields = ["number_of_tracking", "status_of_processing"]
