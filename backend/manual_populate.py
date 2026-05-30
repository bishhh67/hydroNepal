#!/usr/bin/env python
import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydro_basin_api.settings')
django.setup()

from hydro_api.models import RiverBasin, HydropowerProject, SensorData, Alert

print("="*60)
print("STARTING DATABASE POPULATION FOR TRISHULI RIVER BASIN")
print("="*60)

# Clear existing data
print("\n📋 Clearing old data...")
SensorData.objects.all().delete()
Alert.objects.all().delete()
HydropowerProject.objects.all().delete()
RiverBasin.objects.all().delete()
print("✓ Old data cleared")

# Create basin
print("\n🏞️ Creating Trishuli River Basin...")
basin = RiverBasin.objects.create(
    basin_name="Trishuli River Basin",
    river_name="Trishuli River",
    country="Nepal"
)
print(f"✓ Created: {basin.basin_name}, {basin.country}")

# Create hydropower projects IN ORDER (upstream to downstream)
print("\n🏭 Creating Hydropower Projects in sequence...")

# Project 1: Upper Trishuli 1 (Most upstream)
project1 = HydropowerProject.objects.create(
    hydro_name="Upper Trishuli 1",
    basin=basin,
    latitude=28.1000,
    longitude=85.3000,
    installed_capacity_mw=37.6,
    reservoir_capacity=15.2,
    upstream_hydro=None,  # No upstream
    downstream_hydro=None  # Will set later
)
print(f"  ✓ {project1.hydro_name} - 37.6 MW at ({project1.latitude}, {project1.longitude})")

# Project 2: Upper Trishuli 3A
project2 = HydropowerProject.objects.create(
    hydro_name="Upper Trishuli 3A",
    basin=basin,
    latitude=28.0500,
    longitude=85.2500,
    installed_capacity_mw=60.0,
    reservoir_capacity=22.5,
    upstream_hydro=project1,  # Connected to project1
    downstream_hydro=None
)
print(f"  ✓ {project2.hydro_name} - 60.0 MW at ({project2.latitude}, {project2.longitude})")

# Project 3: Trishuli Hydropower
project3 = HydropowerProject.objects.create(
    hydro_name="Trishuli Hydropower",
    basin=basin,
    latitude=27.9500,
    longitude=85.1500,
    installed_capacity_mw=24.0,
    reservoir_capacity=8.5,
    upstream_hydro=project2,
    downstream_hydro=None
)
print(f"  ✓ {project3.hydro_name} - 24.0 MW at ({project3.latitude}, {project3.longitude})")

# Project 4: Devighat Hydropower (Most downstream)
project4 = HydropowerProject.objects.create(
    hydro_name="Devighat Hydropower",
    basin=basin,
    latitude=27.8500,
    longitude=85.1000,
    installed_capacity_mw=14.1,
    reservoir_capacity=5.3,
    upstream_hydro=project3,
    downstream_hydro=None
)
print(f"  ✓ {project4.hydro_name} - 14.1 MW at ({project4.latitude}, {project4.longitude})")

# Set downstream relationships
project1.downstream_hydro = project2
project1.save()
project2.downstream_hydro = project3
project2.save()
project3.downstream_hydro = project4
project3.save()

print("\n📊 Flow Relationship:")
print(f"  Upper Trishuli 1")
print(f"       ↓ shares flow + sediment data")
print(f"  Upper Trishuli 3A")
print(f"       ↓ predicts downstream surge")
print(f"  Trishuli Hydropower")
print(f"       ↓ sends turbine status")
print(f"  Devighat Hydropower")

# Generate sensor data for each project
print("\n📈 Generating sensor data (48 hours per station)...")
projects = [project1, project2, project3, project4]

for idx, project in enumerate(projects):
    print(f"\n  📊 {project.hydro_name}:")
    
    # Base values decrease as we go downstream
    base_inflow = 300 - (idx * 60)
    base_outflow = 280 - (idx * 55)
    base_power = project.installed_capacity_mw * 0.7
    
    # Generate 48 readings (2 days of hourly data)
    for hour in range(48):
        timestamp = datetime.now() - timedelta(hours=47-hour)
        
        # Add realistic variation
        inflow = max(50, base_inflow + random.randint(-50, 70))
        outflow = max(40, base_outflow + random.randint(-45, 65))
        power = max(3, base_power + random.randint(-15, 25))
        power = min(power, project.installed_capacity_mw)
        
        # Create sensor reading
        sensor = SensorData(
            hydro=project,
            timestamp=timestamp,
            # Operational
            water_inflow_m3s=round(inflow, 1),
            water_outflow_m3s=round(outflow, 1),
            reservoir_level_m=round(random.uniform(35, 92), 1),
            turbine_discharge_m3s=round(outflow * 0.85, 1),
            spillway_release_m3s=round(max(0, outflow * 0.15), 1),
            power_generation_mw=round(power, 2),
            turbine_efficiency_percent=round(random.uniform(72, 94), 1),
            gate_opening_percent=round(random.uniform(30, 85), 1),
            # Environmental
            rainfall_mm=round(random.uniform(0, 45), 1),
            sediment_load_ppm=round(random.uniform(150, 750), 1),
            water_temperature_c=round(random.uniform(12, 23), 1),
            ph_level=round(random.uniform(6.5, 8.4), 1),
            turbidity_ntu=round(random.uniform(3, 22), 1),
            dissolved_oxygen_mgL=round(random.uniform(5.5, 9.5), 1),
            humidity_percent=round(random.uniform(45, 88), 1),
            wind_speed_kmh=round(random.uniform(0, 22), 1),
            # Safety
            vibration_level=round(random.uniform(0.3, 4.5), 2),
            seismic_activity_level=round(random.uniform(0, 1.3), 2),
            flood_risk_level=round(random.uniform(0, 8.5), 1),
            dam_stress_level=round(random.uniform(2, 7.5), 1),
            # Status
            turbine_status=random.choice(['Operational', 'Operational', 'Operational', 'Warning']),
            plant_status=random.choice(['Active', 'Active', 'Active', 'Maintenance']),
            sensor_health_status=random.choice(['Healthy', 'Healthy', 'Healthy', 'Degraded'])
        )
        sensor.save()
    
    print(f"    ✓ Generated 48 sensor readings")

# Generate alerts based on sensor thresholds
print("\n⚠️ Generating alerts based on sensor thresholds...")
total_alerts = 0

for project in projects:
    latest = SensorData.objects.filter(hydro=project).order_by('-timestamp').first()
    
    if not latest:
        continue
    
    alerts_created = []
    
    # Check turbine efficiency
    if latest.turbine_efficiency_percent < 70:
        alerts_created.append(Alert(
            hydro=project,
            alert_type="Low Turbine Efficiency",
            severity="High",
            message=f"⚠️ Turbine efficiency dropped to {latest.turbine_efficiency_percent}% - below operational minimum"
        ))
    
    # Check sediment load
    if latest.sediment_load_ppm > 600:
        alerts_created.append(Alert(
            hydro=project,
            alert_type="Critical Sediment Load",
            severity="Critical",
            message=f"⚠️ CRITICAL: Sediment load at {latest.sediment_load_ppm} ppm - immediate turbine inspection needed"
        ))
    elif latest.sediment_load_ppm > 450:
        alerts_created.append(Alert(
            hydro=project,
            alert_type="High Sediment Load",
            severity="High",
            message=f"⚠️ High sediment load: {latest.sediment_load_ppm} ppm - above normal range"
        ))
    
    # Check pH level
    if latest.ph_level < 6.0 or latest.ph_level > 9.0:
        alerts_created.append(Alert(
            hydro=project,
            alert_type="Water Quality Critical",
            severity="Critical",
            message=f"⚠️ CRITICAL: pH level {latest.ph_level} - water quality severely degraded"
        ))
    elif latest.ph_level < 6.5 or latest.ph_level > 8.5:
        alerts_created.append(Alert(
            hydro=project,
            alert_type="Water Quality Alert",
            severity="Medium",
            message=f"⚠️ pH level {latest.ph_level} - outside normal range (6.5-8.5)"
        ))
    
    # Check dissolved oxygen
    if latest.dissolved_oxygen_mgL < 4:
        alerts_created.append(Alert(
            hydro=project,
            alert_type="Critical Low Oxygen",
            severity="Critical",
            message=f"⚠️ CRITICAL: Dissolved oxygen at {latest.dissolved_oxygen_mgL} mg/L - aquatic life at risk"
        ))
    elif latest.dissolved_oxygen_mgL < 5.5:
        alerts_created.append(Alert(
            hydro=project,
            alert_type="Low Oxygen Warning",
            severity="High",
            message=f"⚠️ Low dissolved oxygen: {latest.dissolved_oxygen_mgL} mg/L - below normal"
        ))
    
    # Check flood risk
    if latest.flood_risk_level > 7:
        alerts_created.append(Alert(
            hydro=project,
            alert_type="Severe Flood Risk",
            severity="Critical",
            message=f"⚠️ CRITICAL: Flood risk level {latest.flood_risk_level}/10 - immediate evacuation preparation needed"
        ))
    elif latest.flood_risk_level > 5:
        alerts_created.append(Alert(
            hydro=project,
            alert_type="Flood Risk Warning",
            severity="High",
            message=f"⚠️ High flood risk: {latest.flood_risk_level}/10 - increased water levels expected downstream"
        ))
    
    # Check dam stress
    if latest.dam_stress_level > 7:
        alerts_created.append(Alert(
            hydro=project,
            alert_type="Dam Structure Alert",
            severity="Critical",
            message=f"⚠️ CRITICAL: Dam stress level {latest.dam_stress_level}/10 - structural inspection required immediately"
        ))
    elif latest.dam_stress_level > 5:
        alerts_created.append(Alert(
            hydro=project,
            alert_type="Dam Stress Warning",
            severity="High",
            message=f"⚠️ Elevated dam stress: {latest.dam_stress_level}/10 - monitor closely"
        ))
    
    # Check vibration
    if latest.vibration_level > 4:
        alerts_created.append(Alert(
            hydro=project,
            alert_type="Excessive Vibration",
            severity="High",
            message=f"⚠️ Excessive vibration: {latest.vibration_level} - possible equipment malfunction"
        ))
    elif latest.vibration_level > 3:
        alerts_created.append(Alert(
            hydro=project,
            alert_type="Elevated Vibration",
            severity="Medium",
            message=f"⚠️ Elevated vibration: {latest.vibration_level} - monitor turbine condition"
        ))
    
    # Check turbidity
    if latest.turbidity_ntu > 20:
        alerts_created.append(Alert(
            hydro=project,
            alert_type="High Turbidity",
            severity="Medium",
            message=f"⚠️ High water turbidity: {latest.turbidity_ntu} NTU - reduced water clarity"
        ))
    
    # Check for upstream impact (downstream station gets alerts from upstream issues)
    if project.upstream_hydro:
        upstream_latest = SensorData.objects.filter(hydro=project.upstream_hydro).order_by('-timestamp').first()
        if upstream_latest and upstream_latest.water_outflow_m3s > 350:
            alerts_created.append(Alert(
                hydro=project,
                alert_type="Upstream Discharge Warning",
                severity="High",
                message=f"⚠️ High discharge ({upstream_latest.water_outflow_m3s} m³/s) from {project.upstream_hydro.hydro_name} - prepare for increased flow"
            ))
    
    # Save all alerts
    for alert in alerts_created:
        alert.timestamp = datetime.now() - timedelta(hours=random.randint(1, 48))
        alert.save()
        total_alerts += 1
    
    print(f"  ✓ {project.hydro_name}: {len(alerts_created)} alerts generated")

# Final summary
print("\n" + "="*60)
print("✅ DATABASE POPULATION COMPLETE!")
print("="*60)
print(f"\n📍 BASIN: Trishuli River Basin, Nepal")
print(f"\n🏭 HYDROPOWER PROJECTS (4 stations):")
for p in projects:
    upstream_name = p.upstream_hydro.hydro_name if p.upstream_hydro else "START (upstream)"
    downstream_name = p.downstream_hydro.hydro_name if p.downstream_hydro else "END (downstream)"
    print(f"  • {p.hydro_name}")
    print(f"      ↑ {upstream_name}")
    print(f"      ↓ {downstream_name}")
    print(f"      📊 Capacity: {p.installed_capacity_mw} MW")
    print(f"      📈 Sensor readings: {p.sensor_data.count()}")
    print(f"      ⚠️ Alerts: {p.alerts.count()}")
    print()

print(f"📊 TOTAL STATISTICS:")
print(f"  • Sensor readings: {SensorData.objects.count()}")
print(f"  • Active alerts: {Alert.objects.count()}")
print("="*60)
print("\n🎯 You can now run: python manage.py runserver")
print("🌐 Then open: http://localhost:3000")
print("="*60)

