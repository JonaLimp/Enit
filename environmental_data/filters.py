import django_filters
from .models import HistoricalEnvironmentalRecord
from django.db.models import Max
from django_filters import rest_framework as filters


class HistoricalDataFilter(django_filters.FilterSet):
    """
    A FilterSet for filtering historical environmental records.
    If no year range is provided, it fetches data for the most recent year.
    """

    country = filters.BaseInFilter(
        field_name="country__code", lookup_expr="in", label="Country Codes"
    )
    substance = django_filters.CharFilter(
        field_name="substance__name", lookup_expr="iexact"
    )
    sector = django_filters.CharFilter(field_name="sector__name", lookup_expr="iexact")

    start_year = django_filters.NumberFilter(field_name="year", lookup_expr="gte")
    end_year = django_filters.NumberFilter(field_name="year", lookup_expr="lte")

    class Meta:
        model = HistoricalEnvironmentalRecord
        fields = ["country", "substance", "sector", "start_year", "end_year"]

    @property
    def qs(self):
        """
        Custom queryset behavior to use the most recent yea
        r if no year range is specified.
        """
        queryset = super().qs
        start_year = self.data.get("start_year")
        end_year = self.data.get("end_year")

        if not start_year or not end_year:
            most_recent_year = queryset.aggregate(max_year=Max("year"))["max_year"]
            if most_recent_year is not None:
                queryset = queryset.filter(year=most_recent_year)

        return queryset
