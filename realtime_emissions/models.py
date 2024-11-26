from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self) -> str:
        return self.name


class RealtimeEmissionRecord(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    carbon_intensity: float = models.FloatField()
    timestamp = models.DateTimeField(null=False, blank=False)

    class Meta:
        unique_together = ("region", "timestamp")
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.region} - {self.timestamp}"
