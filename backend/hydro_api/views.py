from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.db.models import Avg
from datetime import datetime, timedelta
from .models import HydropowerProject, SensorData, Alert , ESPData , TurbineMonitoring
from .serializers import *

from django.views.decorators.csrf import csrf_exempt
from .ai_model import predict_turbine_behavior, calculate_flood_risk


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




@csrf_exempt  # ADD THIS LINE
@api_view(['POST'])
def receive_esp_data(request):
    """Receive distance and current from ESP"""
    print("=" * 50)  # ADD THIS FOR DEBUGGING
    print("ESP DATA RECEIVED!")  # ADD THIS FOR DEBUGGING
    print("Data:", request.data)  # ADD THIS FOR DEBUGGING
    print("=" * 50)  # ADD THIS FOR DEBUGGING
    
    try:
        data = request.data
        device_id = data.get('device_id')
        
        # Map device_id to your hydropower projects
        mapping = {
            'hydro1': 'Upper Trishuli 1',
            'hydro2': 'Upper Trishuli 3A', 
            'hydro3': 'Trishuli Hydropower',
            'hydro4': 'Devighat Hydropower'
        }
        
        hydro_name = mapping.get(device_id)
        if not hydro_name:
            return Response({'error': 'Unknown device'}, status=400)
        
        project = HydropowerProject.objects.get(hydro_name=hydro_name)
        
        # Save ESP data
        esp_reading = ESPData.objects.create(
            hydro=project,
            distance_cm=float(data.get('distance', 0)),
            current_amps=float(data.get('current', 0))
        )
        

         # ========== ADD THIS TO SHOW SAVED DATA ==========
        print(f"✅ SAVED to Database:")
        print(f"   • Hydro: {project.hydro_name}")
        print(f"   • Distance: {distance} cm")
        print(f"   • Current: {current} A")
        print(f"   • Record ID: {esp_reading.id}")
        print("="*60 + "\n")


        return Response({'status': 'success', 'id': esp_reading.id}, status=201)
        
    except Exception as e:
        print("ERROR:", str(e))  # ADD THIS FOR DEBUGGING
        return Response({'error': str(e)}, status=500)
    


@api_view(['GET'])
def get_esp_data(request, hydro_id=None):
    """Get latest ESP readings"""
    if hydro_id:
        data = ESPData.objects.filter(hydro_id=hydro_id).first()
    else:
        # Get latest for each hydro
        projects = HydropowerProject.objects.all()
        data = []
        for p in projects:
            latest = p.esp_readings.first()
            if latest:
                data.append(latest)
    
    from .serializers import ESPDataSerializer
    serializer = ESPDataSerializer(data, many=not hydro_id)
    return Response(serializer.data)



@api_view(['GET'])
def get_prediction_data(request, hydro_id=None):
    """Get flood risk and turbine prediction for latest ESP data"""
    
    if hydro_id:
        # Get latest ESP reading for specific hydro
        esp_data = ESPData.objects.filter(hydro_id=hydro_id).first()
        if not esp_data:
            return Response({'error': 'No ESP data found'}, status=404)
        data_list = [esp_data]
    else:
        # Get latest for each hydro
        projects = HydropowerProject.objects.all()
        data_list = []
        for p in projects:
            latest = p.esp_readings.first()
            if latest:
                data_list.append(latest)
    
    results = []
    current_time = datetime.now()
    
    for esp in data_list:
        # Calculate flood risk from distance
        flood_data = calculate_flood_risk(esp.distance_cm, esp.current_amps)
        
        # Predict turbine behavior from current
        is_abnormal, confidence = predict_turbine_behavior(
            month=current_time.month,
            day=current_time.day,
            hour=current_time.hour,
            current=esp.current_amps
        )
        
        results.append({
            'hydro_id': esp.hydro.hydro_id,
            'hydro_name': esp.hydro.hydro_name,
            'distance_cm': esp.distance_cm,
            'current_amps': esp.current_amps,
            'timestamp': esp.timestamp,
            'flood_risk': flood_data,
            'turbine': {
                'is_abnormal': is_abnormal,
                'confidence': round(confidence * 100, 1) if confidence else 0,
                'status': '⚠️ ABNORMAL' if is_abnormal else '✅ NORMAL',
                'message': 'Turbine showing abnormal behavior. Inspection recommended.' if is_abnormal 
                          else 'Turbine operating within normal parameters.'
            }
        })
    
    if hydro_id and results:
        return Response(results[0])
    return Response(results)


@api_view(['POST'])
def manual_predict(request):
    """Manual prediction endpoint for testing"""
    try:
        data = request.data
        distance = float(data.get('distance', 0))
        current = float(data.get('current', 0))
        
        flood_data = calculate_flood_risk(distance, current)
        now = datetime.now()
        is_abnormal, confidence = predict_turbine_behavior(
            month=now.month,
            day=now.day,
            hour=now.hour,
            current=current
        )
        
        return Response({
            'flood_risk': flood_data,
            'turbine': {
                'is_abnormal': is_abnormal,
                'confidence': round(confidence * 100, 1) if confidence else 0,
                'status': '⚠️ ABNORMAL' if is_abnormal else '✅ NORMAL'
            }
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    


@api_view(['GET', 'POST'])
def receive_turbine_data(request):
    """Receive turbine monitoring data from ESP or return turbine records."""
    if request.method == 'GET':
        hydro_id = request.query_params.get('hydro_id')
        if hydro_id:
            data = TurbineMonitoring.objects.filter(hydro_id=hydro_id).order_by('-timestamp').first()
            if not data:
                return Response([], status=200)
            serializer = TurbineMonitoringSerializer(data)
            return Response([serializer.data])

        projects = HydropowerProject.objects.all()
        latest_records = []
        for project in projects:
            latest = project.turbine_readings.first()
            if latest:
                latest_records.append(latest)

        serializer = TurbineMonitoringSerializer(latest_records, many=True)
        return Response(serializer.data)

    try:
        data = request.data
        device_id = data.get('device_id')
        
        mapping = {
            'hydro1': 'Upper Trishuli 1',
            'hydro2': 'Upper Trishuli 3A',
            'hydro3': 'Trishuli Hydropower',
            'hydro4': 'Devighat Hydropower'
        }
        
        hydro_name = mapping.get(device_id)
        if not hydro_name:
            return Response({'error': 'Unknown device'}, status=400)
        
        project = HydropowerProject.objects.get(hydro_name=hydro_name)
        
        turbine_data = TurbineMonitoring.objects.create(
            hydro=project,
            turbine_rpm=float(data.get('turbine_rpm', 0)),
            vibration_level=float(data.get('vibration_level', 0)),
            bearing_temperature_c=float(data.get('bearing_temperature', 0)),
            oil_leakage_status=data.get('oil_leakage', 'Normal'),
            lubrication_status=data.get('lubrication', 'Optimal'),
            turbine_efficiency=float(data.get('turbine_efficiency', 85)),
            power_output_mw=float(data.get('power_output', 0))
        )
        
        return Response({'status': 'success', 'id': turbine_data.monitoring_id}, status=201)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def get_turbine_data(request, hydro_id=None):
    """Get latest turbine monitoring data"""
    if hydro_id:
        data = TurbineMonitoring.objects.filter(hydro_id=hydro_id).first()
        if not data:
            return Response([], status=200)
        serializer = TurbineMonitoringSerializer(data)
        return Response([serializer.data])
    else:
        projects = HydropowerProject.objects.all()
        data = []
        for p in projects:
            latest = p.turbine_readings.first()
            if latest:
                data.append(latest)
        serializer = TurbineMonitoringSerializer(data, many=True)
        return Response(serializer.data)
