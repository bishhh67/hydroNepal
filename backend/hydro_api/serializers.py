from rest_framework import serializers
from .models import RiverBasin, HydropowerProject, SensorData, Alert

class RiverBasinSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiverBasin
        fields = '__all__'

class HydropowerProjectSerializer(serializers.ModelSerializer):
    upstream_name = serializers.CharField(source='upstream_hydro.hydro_name', read_only=True)
    downstream_name = serializers.CharField(source='downstream_hydro.hydro_name', read_only=True)
    
    class Meta:
        model = HydropowerProject
        fields = '__all__'

class SensorDataSerializer(serializers.ModelSerializer):
    hydro_name = serializers.CharField(source='hydro.hydro_name', read_only=True)
    value_statuses = serializers.SerializerMethodField()
    
    class Meta:
        model = SensorData
        fields = '__all__'
    
    def get_value_statuses(self, obj):
        """Return status for each sensor value"""
        statuses = {}
        fields = ['ph_level', 'water_temperature_c', 'dissolved_oxygen_mgL', 'turbidity_ntu', 
                  'sediment_load_ppm', 'turbine_efficiency_percent', 'reservoir_level_m',
                  'vibration_level', 'dam_stress_level', 'flood_risk_level']
        
        for field in fields:
            value = getattr(obj, field, None)
            if value is not None:
                statuses[field] = obj.get_status_for_value(field, value)
        
        return statuses

class AlertSerializer(serializers.ModelSerializer):
    hydro_name = serializers.CharField(source='hydro.hydro_name', read_only=True)
    
    class Meta:
        model = Alert
        fields = '__all__'



class ESPDataSerializer(serializers.ModelSerializer):
    hydro_name = serializers.CharField(source='hydro.hydro_name', read_only=True)
    
    class Meta:
        from .models import ESPData
        model = ESPData
        fields = ['id', 'hydro_name', 'distance_cm', 'current_amps', 'timestamp']


class TurbineMonitoringSerializer(serializers.ModelSerializer):
    hydro_name = serializers.CharField(source='hydro.hydro_name', read_only=True)
    
    class Meta:
        from .models import TurbineMonitoring
        model = TurbineMonitoring
        fields = '__all__'