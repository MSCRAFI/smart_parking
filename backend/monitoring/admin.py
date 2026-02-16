from django.contrib import admin
from .models import ParkingZone, Device, TelemetryData, ParkingLog, Alert

@admin.register(ParkingZone)
class ParkingZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'total_slots', 'daily_target']
    search_fields = ['name', 'code']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['device_code', 'zone', 'slot_number', 'is_active', 'last_seen']
    list_filter = ['zone', 'is_active']
    search_fields = ['device_code', 'slot_number']

@admin.register(TelemetryData)
class TelemetryDataAdmin(admin.ModelAdmin):
    list_display = ['device', 'timestamp', 'voltage', 'current', 'power_factor']
    list_filter = ['timestamp']
    search_fields = ['device__device_code']

@admin.register(ParkingLog)
class ParkingLogAdmin(admin.ModelAdmin):
    list_display = ['device', 'is_occupied', 'timestamp']
    list_filter = ['is_occupied', 'timestamp']
    search_fields = ['device__device_code']

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['device', 'severity', 'alert_type', 'is_acknowledged', 'created_at']
    list_filter = ['severity', 'alert_type', 'is_acknowledged']
    search_fields = ['device__device_code', 'message']
    actions = ['mark_acknowledged']
    
    def mark_acknowledged(self, request, queryset):
        queryset.update(is_acknowledged=True)
    mark_acknowledged.short_description = "Mark selected alerts as acknowledged"