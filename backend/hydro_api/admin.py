from django.contrib import admin
from .models import RiverBasin, HydropowerProject, SensorData, Alert

admin.site.register(RiverBasin)
admin.site.register(HydropowerProject)
admin.site.register(SensorData)
admin.site.register(Alert)