from django.urls import path
from . import views

urlpatterns = [
    path('hydropower/', views.hydropower_list, name='hydropower-list'),
    path('sensor-data/<int:hydro_id>/', views.sensor_data_detail, name='sensor-data-detail'),
    path('sensor-trends/<int:hydro_id>/', views.sensor_trends, name='sensor-trends'),
    path('alerts/', views.alerts_list, name='alerts-list'),
    path('basin-map-data/', views.basin_map_data, name='basin-map-data'),
]