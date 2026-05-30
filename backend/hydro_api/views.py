from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Avg
from datetime import datetime, timedelta
from .models import HydropowerProject, SensorData, Alert
from .serializers import *

@api_view(['GET'])
def hydropower_list(request):
    """Get all hydropower projects with their relationships"""
    projects = HydropowerProject.objects.all()
    serializer = HydropowerProjectSerializer(projects, many=True)
    print(f"Returning {len(projects)} projects")  # Debug
    return Response(serializer.data)

@api_view(['GET'])
def sensor_data_detail(request, hydro_id):
    """Get latest sensor data for a specific hydro"""
    try:
        sensor_data = SensorData.objects.filter(hydro_id=hydro_id).first()
        if sensor_data:
            serializer = SensorDataSerializer(sensor_data)
            return Response(serializer.data)
        else:
            return Response({'error': 'No sensor data found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def sensor_trends(request, hydro_id):
    """Get last 24 hours of sensor data"""
    data = SensorData.objects.filter(hydro_id=hydro_id).order_by('timestamp')[:24]
    serializer = SensorDataSerializer(data, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def alerts_list(request):
    """Get all alerts"""
    alerts = Alert.objects.all().order_by('-timestamp')[:20]
    serializer = AlertSerializer(alerts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def basin_map_data(request):
    """Get data for map visualization"""
    projects = HydropowerProject.objects.all()
    result = []
    for project in projects:
        latest_sensor = project.sensor_data.first()
        alert_count = Alert.objects.filter(hydro=project, severity__in=['High', 'Critical']).count()
        
        result.append({
            'id': project.hydro_id,
            'name': project.hydro_name,
            'latitude': float(project.latitude),
            'longitude': float(project.longitude),
            'installed_capacity_mw': float(project.installed_capacity_mw),
            'upstream_id': project.upstream_hydro_id,
            'downstream_id': project.downstream_hydro_id,
            'current_power': float(latest_sensor.power_generation_mw) if latest_sensor else 0,
            'water_inflow': float(latest_sensor.water_inflow_m3s) if latest_sensor else 0,
            'water_outflow': float(latest_sensor.water_outflow_m3s) if latest_sensor else 0,
            'reservoir_level': float(latest_sensor.reservoir_level_m) if latest_sensor else 0,
            'alert_count': alert_count
        })
    return Response(result)