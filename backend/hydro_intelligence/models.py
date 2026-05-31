from django.db import models

class TelemetryLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    river_stage = models.FloatField()
    discharge = models.FloatField()
    sediment_concentration = models.FloatField()
    distance = models.FloatField()
    elevation_drop = models.FloatField(default=45.0)
    velocity = models.FloatField()
    time_to_reach = models.FloatField()
    flood_risk = models.CharField(max_length=20)
    sediment_risk = models.CharField(max_length=20)
    status = models.CharField(max_length=20)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Telemetry Log at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - Status: {self.status}"