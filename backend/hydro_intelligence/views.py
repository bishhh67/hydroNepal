import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import TelemetryLog

@api_view(['GET'])
def get_intelligence_data(request):
    """Get recent telemetry logs for React frontend"""
    recent_logs = TelemetryLog.objects.all()[:50]
    data = []
    for log in recent_logs:
        data.append({
            'id': log.id,
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'river_stage': log.river_stage,
            'discharge': log.discharge,
            'sediment_concentration': log.sediment_concentration,
            'distance': log.distance,
            'elevation_drop': log.elevation_drop,
            'velocity': log.velocity,
            'time_to_reach': log.time_to_reach,
            'flood_risk': log.flood_risk,
            'sediment_risk': log.sediment_risk,
            'status': log.status
        })
    return Response(data)

@api_view(['POST'])
@csrf_exempt
def save_intelligence_log(request):
    """Save telemetry log from React frontend"""
    try:
        data = request.data
        log = TelemetryLog.objects.create(
            river_stage=float(data.get('river_stage')),
            discharge=float(data.get('discharge')),
            sediment_concentration=float(data.get('sediment_concentration')),
            distance=float(data.get('distance')),
            elevation_drop=float(data.get('elevation_drop', 45.0)),
            velocity=float(data.get('velocity')),
            time_to_reach=float(data.get('time_to_reach')),
            flood_risk=data.get('flood_risk'),
            sediment_risk=data.get('sediment_risk'),
            status=data.get('status')
        )
        return Response({
            'status': 'success',
            'message': 'Telemetry snapshot successfully logged',
            'id': log.id,
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }, status=201)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)

@api_view(['DELETE'])
def delete_intelligence_log(request, log_id):
    """Delete a telemetry log"""
    try:
        log = TelemetryLog.objects.get(id=log_id)
        log.delete()
        return Response({'status': 'success', 'message': 'Log deleted'})
    except TelemetryLog.DoesNotExist:
        return Response({'status': 'error', 'message': 'Log not found'}, status=404)