import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    has_discount = django_filters.BooleanFilter(method='filter_has_discount')

    class Meta:
        model = Product
        fields = ['category', 'is_featured', 'is_new', 'unit']

    def filter_in_stock(self, queryset, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset.filter(stock=0)

    def filter_has_discount(self, queryset, value):
        if value:
            return queryset.filter(old_price__isnull=False)
        return queryset