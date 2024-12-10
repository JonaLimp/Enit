import django_filters
from .models import HistoricalEnvironmentalRecord


class HistoricalDataFilter(django_filters.FilterSet):

    region_code = django_filters.CharFilter(
        field_name="region__code", lookup_expr="iexact"
    )

    substance = django_filters.CharFilter(
        field_name="substance__name", lookup_expr="iexact"
    )

    sector = django_filters.CharFilter(field_name="sector__name", lookup_expr="iexact")

    start_year = django_filters.NumberFilter(field_name="year", lookup_expr="gte")

    end_year = django_filters.NumberFilter(field_name="year", lookup_expr="lte")

    class Meta:
        model = HistoricalEnvironmentalRecord
        fields = ["region_code", "substance", "sector", "start_year", "end_year"]
