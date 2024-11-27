from django.db import models
from ..enit.models import Region


class RealtimeEmissionRecord(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    carbon_intensity: float = models.FloatField()
    timestamp = models.DateTimeField(null=False, blank=False)

    class Meta:
        unique_together = ("region", "timestamp")
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.region} - {self.timestamp}"
