#!/usr/bin/env python
import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydro_basin_api.settings')
django.setup()

from hydro_api.models import HydropowerProject, TurbineMonitoring

print("="*60)
print("POPULATING TURBINE MONITORING DATA")
print("="*60)

# Get all hydropower projects
projects = HydropowerProject.objects.all()

if projects.count() == 0:
    print("No hydropower projects found! Run manual_populate.py first.")
    exit()

# Clear existing turbine data
TurbineMonitoring.objects.all().delete()
print("Cleared existing turbine data")

# Turbine data for each hydro
turbine_data = {
    'Upper Trishuli 1': {
        'turbine_rpm': 1350,
        'vibration_level': 4.5,
        'bearing_temperature_c': 72,
        'oil_leakage_status': 'Minor',
        'lubrication_status': 'Low',
        'turbine_efficiency': 78,
        'power_output_mw': 28.5
    },
    'Upper Trishuli 3A': {
        'turbine_rpm': 1420,
        'vibration_level': 5.2,
        'bearing_temperature_c': 78,
        'oil_leakage_status': 'Moderate',
        'lubrication_status': 'Critical',
        'turbine_efficiency': 72,
        'power_output_mw': 45.0
    },
    'Trishuli Hydropower': {
        'turbine_rpm': 890,
        'vibration_level': 2.1,
        'bearing_temperature_c': 55,
        'oil_leakage_status': 'Normal',
        'lubrication_status': 'Optimal',
        'turbine_efficiency': 88,
        'power_output_mw': 19.5
    },
    'Devighat Hydropower': {
        'turbine_rpm': 780,
        'vibration_level': 1.8,
        'bearing_temperature_c': 48,
        'oil_leakage_status': 'Normal',
        'lubrication_status': 'Optimal',
        'turbine_efficiency': 91,
        'power_output_mw': 12.8
    }
}

print("\n📊 Adding turbine monitoring data...")

for project in projects:
    if project.hydro_name in turbine_data:
        data = turbine_data[project.hydro_name]
        
        # Create turbine monitoring record
        turbine = TurbineMonitoring.objects.create(
            hydro=project,
            turbine_rpm=data['turbine_rpm'],
            vibration_level=data['vibration_level'],
            bearing_temperature_c=data['bearing_temperature_c'],
            oil_leakage_status=data['oil_leakage_status'],
            lubrication_status=data['lubrication_status'],
            turbine_efficiency=data['turbine_efficiency'],
            power_output_mw=data['power_output_mw']
        )
        
        print(f"  ✓ {project.hydro_name}")
        print(f"      RPM: {data['turbine_rpm']} | Vibration: {data['vibration_level']} | Temp: {data['bearing_temperature_c']}°C")
        print(f"      Oil: {data['oil_leakage_status']} | Lubrication: {data['lubrication_status']}")
        print(f"      Efficiency: {data['turbine_efficiency']}% | Power: {data['power_output_mw']} MW")
        print()

print("="*60)
print(f"✅ Added {TurbineMonitoring.objects.count()} turbine monitoring records")
print("="*60)