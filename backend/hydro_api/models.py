from django.db import models

class RiverBasin(models.Model):
    basin_id = models.AutoField(primary_key=True)
    basin_name = models.CharField(max_length=100)
    river_name = models.CharField(max_length=100)
    country = models.CharField(max_length=50, default='Nepal')
    
    def __str__(self):
        return self.basin_name

class HydropowerProject(models.Model):
    hydro_id = models.AutoField(primary_key=True)
    hydro_name = models.CharField(max_length=100)
    basin = models.ForeignKey(RiverBasin, on_delete=models.CASCADE, related_name='projects')
    latitude = models.FloatField()
    longitude = models.FloatField()
    installed_capacity_mw = models.FloatField()
    reservoir_capacity = models.FloatField(help_text="Million cubic meters")
    upstream_hydro = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='downstream_projects')
    downstream_hydro = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='upstream_projects')
    
    def __str__(self):
        return self.hydro_name

class SensorData(models.Model):
    sensor_id = models.AutoField(primary_key=True)
    hydro = models.ForeignKey(HydropowerProject, on_delete=models.CASCADE, related_name='sensor_data')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Operational Variables
    water_inflow_m3s = models.FloatField(default=0)
    water_outflow_m3s = models.FloatField(default=0)
    reservoir_level_m = models.FloatField(default=0)
    turbine_discharge_m3s = models.FloatField(default=0)
    spillway_release_m3s = models.FloatField(default=0)
    power_generation_mw = models.FloatField(default=0)
    turbine_efficiency_percent = models.FloatField(default=85)
    gate_opening_percent = models.FloatField(default=0)
    
    # Environmental Variables
    rainfall_mm = models.FloatField(default=0)
    sediment_load_ppm = models.FloatField(default=0)
    water_temperature_c = models.FloatField(default=15)
    ph_level = models.FloatField(default=7.0)
    turbidity_ntu = models.FloatField(default=5)
    dissolved_oxygen_mgL = models.FloatField(default=8)
    humidity_percent = models.FloatField(default=60)
    wind_speed_kmh = models.FloatField(default=10)
    
    # Safety Variables
    vibration_level = models.FloatField(default=0.5)
    seismic_activity_level = models.FloatField(default=0)
    flood_risk_level = models.FloatField(default=0)
    dam_stress_level = models.FloatField(default=0)
    
    # System Variables
    turbine_status = models.CharField(max_length=20, default='Operational')
    plant_status = models.CharField(max_length=20, default='Active')
    sensor_health_status = models.CharField(max_length=20, default='Healthy')
    
    class Meta:
        ordering = ['-timestamp']
    
    def get_status_for_value(self, field_name, value):
        """Determine if a value is Normal, Below Normal, or Above Normal"""
        thresholds = {
            'ph_level': {'min': 6.5, 'max': 8.5, 'normal_min': 6.8, 'normal_max': 8.2},
            'water_temperature_c': {'min': 0, 'max': 30, 'normal_min': 10, 'normal_max': 20},
            'dissolved_oxygen_mgL': {'min': 0, 'max': 15, 'normal_min': 6, 'normal_max': 12},
            'turbidity_ntu': {'min': 0, 'max': 100, 'normal_min': 0, 'normal_max': 10},
            'sediment_load_ppm': {'min': 0, 'max': 2000, 'normal_min': 0, 'normal_max': 300},
            'turbine_efficiency_percent': {'min': 0, 'max': 100, 'normal_min': 80, 'normal_max': 95},
            'reservoir_level_m': {'min': 0, 'max': 100, 'normal_min': 40, 'normal_max': 85},
            'vibration_level': {'min': 0, 'max': 10, 'normal_min': 0, 'normal_max': 3},
            'dam_stress_level': {'min': 0, 'max': 10, 'normal_min': 0, 'normal_max': 5},
            'flood_risk_level': {'min': 0, 'max': 10, 'normal_min': 0, 'normal_max': 4},
        }
        
        if field_name in thresholds:
            t = thresholds[field_name]
            if value < t['normal_min']:
                return 'below_normal'
            elif value > t['normal_max']:
                return 'above_normal'
            else:
                return 'normal'
        return 'normal'

class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    
    alert_id = models.AutoField(primary_key=True)
    hydro = models.ForeignKey(HydropowerProject, on_delete=models.CASCADE, related_name='alerts')
    timestamp = models.DateTimeField(auto_now_add=True)
    alert_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    message = models.TextField()
    
    class Meta:
        ordering = ['-timestamp']



class ESPData(models.Model):
    id = models.AutoField(primary_key=True)
    hydro = models.ForeignKey(HydropowerProject, on_delete=models.CASCADE, related_name='esp_readings')
    distance_cm = models.FloatField(default=0)
    current_amps = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']



class TurbineMonitoring(models.Model):
    monitoring_id = models.AutoField(primary_key=True)
    hydro = models.ForeignKey(HydropowerProject, on_delete=models.CASCADE, related_name='turbine_readings')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Turbine Parameters
    turbine_rpm = models.FloatField(default=0, help_text="Turbine rotation speed in RPM")
    vibration_level = models.FloatField(default=0, help_text="Vibration level 0-10")
    bearing_temperature_c = models.FloatField(default=40, help_text="Bearing temperature in Celsius")
    
    # Oil and Lubrication
    oil_leakage_status = models.CharField(max_length=20, default='Normal', choices=[
        ('Normal', 'Normal'),
        ('Minor', 'Minor Leakage'),
        ('Moderate', 'Moderate Leakage'),
        ('Severe', 'Severe Leakage')
    ])
    lubrication_status = models.CharField(max_length=20, default='Optimal', choices=[
        ('Optimal', 'Optimal'),
        ('Low', 'Low Oil'),
        ('Critical', 'Critical'),
        ('Contaminated', 'Contaminated')
    ])
    
    # Performance
    turbine_efficiency = models.FloatField(default=85, help_text="Current efficiency percentage")
    power_output_mw = models.FloatField(default=0, help_text="Current power output in MW")
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.hydro.hydro_name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"