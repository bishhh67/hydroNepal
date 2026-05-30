from django.urls import path
from . import views

urlpatterns = [
    path('hydropower/', views.hydropower_list, name='hydropower-list'),
    path('sensor-data/<int:hydro_id>/', views.sensor_data_detail, name='sensor-data-detail'),
    path('sensor-trends/<int:hydro_id>/', views.sensor_trends, name='sensor-trends'),
    path('alerts/', views.alerts_list, name='alerts-list'),
    path('basin-map-data/', views.basin_map_data, name='basin-map-data'),

    path('esp-data/', views.receive_esp_data, name='esp-data'),  # POST only
    path('esp-get/', views.get_esp_data, name='get-esp-data'),   # GET only

    path('predictions/', views.get_prediction_data, name='predictions'),
    path('predictions/<int:hydro_id>/', views.get_prediction_data, name='predictions-hydro'),
    path('manual-predict/', views.manual_predict, name='manual-predict'),
    path('turbine-data/', views.receive_turbine_data, name='turbine-data'),
    path('turbine-data/<int:hydro_id>/', views.get_turbine_data, name='get-turbine-data'),
]


