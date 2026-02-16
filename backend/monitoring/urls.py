from django.urls import path
from . import views

urlpatterns = [
    path('telemetry/', views.telemetry_submit, name='telemetry-submit'),
    path('telemetry/bulk/', views.telemetry_bulk_submit, name='telemetry-bulk'),
    path('dashboard/summary/', views.dashboard_summary, name='dashboard-summary'),
    path('parking-log/', views.parking_log_submit, name='parking-log-submit'),
    path('alerts/', views.alerts_list, name='alert-list'),
    path('alerts/<int:pk>/acknowledge/', views.alert_acknowledge, name='alert-acknowledge'),
]
