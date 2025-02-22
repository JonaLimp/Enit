import json
from pathlib import Path
from django.db import models


class Country(models.Model):
    """
    Represents a geographic area (e.g., a country or state).
    """

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Sector(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Substance(models.Model):
    """
    A model for substances, with a unique canonical name.
    """

    name = models.CharField(max_length=100, unique=True)

    @classmethod
    def load_aliases(cls):
        file_path = Path(__file__).parent / "substance_aliases.json"
        with file_path.open("r") as file:
            aliases = json.load(file)
        return aliases

    @classmethod
    def normalize_substance_name(cls, input_name, aliases):
        """
        Normalize the given substance name by checking
        against a dictionary of valid aliases.
        """
        for canonical, aliases in aliases.items():
            if input_name == canonical or input_name in aliases:
                return canonical

        return input_name

    def clean(self):
        """
        Normalize the substance name before saving it to the database.
        """
        aliases = self.load_aliases
        self.name = self.normalize_substance_name(self.name), aliases
        if not self.name:
            raise ValueError(f"Invalid substance name: {self.name}")

    def __str__(self):
        return self.name


class EnvironmentalRecord(models.Model):
    """
    Base model for environmental records, shared across different data types.
    """

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    substance = models.ForeignKey(Substance, on_delete=models.CASCADE)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)

    value = models.FloatField()

    class Meta:
        abstract = True
        unique_together = ("country", "substance", "timestamp")


class RealtimeEnvironmentalRecord(EnvironmentalRecord):
    """
    Model for historical environmental data.
    """

    timestamp = models.DateTimeField(null=False, blank=False)
    record_type = "real_time"

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.country} - {self.substance} - {self.timestamp}"


class HistoricalEnvironmentalRecord(EnvironmentalRecord):
    """

    Model for historical environmental data.
    """

    year = models.IntegerField()
    record_type = "historical"

    class Meta:
        ordering = ["-year"]

    def __str__(self):
        return f"{self.country} - {self.substance} - {self.year}"
