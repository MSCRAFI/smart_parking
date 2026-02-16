from django.urls import path
from . import views

urlpatterns = [
    path('telemetry/', views.telemetry_submit, name='telemetry-submit'),
    path('telemetry/bulk/', views.telemetry_bulk_submit, name='telemetry-bulk'),
]
