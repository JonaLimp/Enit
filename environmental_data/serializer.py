from rest_framework import serializers
from .models import (
    HistoricalEnvironmentalRecord,
    Country,
    Sector,
    Substance,
)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = "__all__"


class SubstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Substance
        fields = "__all__"


class HistoricalEnvironmentalRecordSerializer(serializers.ModelSerializer):
    country = CountrySerializer()
    sector = SectorSerializer()
    substance = SubstanceSerializer()

    class Meta:
        model = HistoricalEnvironmentalRecord
        fields = "__all__"
