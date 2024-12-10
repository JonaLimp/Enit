from rest_framework import serializers
from .models import (
    HistoricalEnvironmentalRecord,
    Region,
    Sector,
    Substance,
)


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
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
    region = RegionSerializer()
    sector = SectorSerializer()
    substance = SubstanceSerializer()

    class Meta:
        model = HistoricalEnvironmentalRecord
        fields = "__all__"
