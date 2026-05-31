from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.get_intelligence_data, name='intelligence-data'),
    path('save/', views.save_intelligence_log, name='save-intelligence'),
    path('delete/<int:log_id>/', views.delete_intelligence_log, name='delete-intelligence'),
]