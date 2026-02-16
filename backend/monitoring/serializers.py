from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Device, TelemetryData, ParkingZone, ParkingLog, Alert
from django.db.models import Count, Q

# serializer for telemetry data sent by devices
class TelemetrySerializer(serializers.Serializer):
    device_code = serializers.CharField(max_length=50)
    voltage = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=0)
    current = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=0)
    power_factor = serializers.DecimalField(max_digits=4, decimal_places=2, min_value=0, max_value=1)
    timestamp = serializers.DateTimeField()

    def validate_device_code(self, value):
        try:
            device = Device.objects.get(device_code=value)
            if not device.is_active:
                raise serializers.ValidationError("Device is inactive.")
            return value
        except Device.DoesNotExist:
            raise serializers.ValidationError("Device does not exist.")
        
    def validate_timestamp(self, value):
        now = timezone.now()
        if value > now:
            raise serializers.ValidationError("Timestamp cannot be in the future.")
        # reject data older than 24 hours
        if value < now - timedelta(hours=24):
            raise serializers.ValidationError("Timestamp is too old. (> 24 hours)")
        return 
    
    def create(self, validated_data):
        device = Device.objects.get(device_code=validated_data['device_code'])
        device.update_last_seen()

        telemetry = TelemetryData.objects.create(
            device=device,
            voltage=validated_data['voltage'],
            current=validated_data['current'],
            power_factor=validated_data['power_factor'],
            timestamp=validated_data['timestamp']
        )

        # logic: check for abnormal power usage
        self._check_power_anomaly(telemetry)

        return telemetry
    
    def _check_power_anomaly(self, telemetry):
        """Alert if power consumption exceeds threshold"""
        power = telemetry.power_consumption
        POWER_THRESHOLD = 1500  # watts

        if power > POWER_THRESHOLD:
            Alert.create_if_not_exists(
                device=telemetry.device,
                alert_type='HIGH_POWER',
                severity='WARNING',
                message=f'Abnormal power usage: {power:.2f}W (threshold: {POWER_THRESHOLD}W)'
            )

# serializer for bulk telemetry data upload
class BulkTelemetrySerializer(serializers.Serializer):
    data = TelemetrySerializer(many=True)

    def create(self, validated_data):
        results = []
        errors = []

        for item in validated_data['data']:
            try:
                serializers = TelemetrySerializer(data=item)
                if serializers.is_valid(raise_exception=True):
                    results.append(serializers.save())
            except Exception as e:
                errors.append(
                    {
                        'device_code': item.get('device_code'),
                        'error': str(e)
                    }
                )
        return {
            'created': len(results),
            'errors': errors
        }
    
class DashboardSummarySerializer(serializers.Serializer):
    date = serializers.DateField(required=False)

    def validate_data(self, value):
        if not value:
            return timezone.now().date()
        return value
    
    def to_representation(self, instance):
        target_data = self.validated_data.get('date', timezone.now().date())
        start_time = timezone.make_aware(datetime.combine(target_data, datetime.min.time()))
        end_time = timezone.make_aware(datetime.combine(target_data, datetime.max.time()))

        # total parking events in a day
        total_events = ParkingLog.objects.filter(timestamp__range=(start_time, end_time)).count()

        # current occupancy (latest status per device)
        from django.db.models import OuterRef, Subquery
        latest_logs = ParkingLog.objects.filter(
            device=OuterRef('pk')
        ).order_by('-timestamp')

        devices_with_status = Device.objects.annotate(
            latest_occupied=Subquery(
                latest_logs.values('is_occupied')[:1]
            )
        )

        current_occupancy = devices_with_status.filter(
            latest_occupied=True
        ).count()

        # active devices (received data in last 2 minutes)
        two_minutes_ago = timezone.now() - timedelta(minutes=2)
        active_devices = Device.objects.filter(
            last_seen__gte=two_minutes_ago
        ).count()

        # alerts triggered today
        alerts_today = Alert.objects.filter(
            created_at__range=(start_time, end_time)
        ).count()

        # Critical alerts count
        critical_alerts = Alert.objects.filter(
            created_at__range=(start_time, end_time),
            severity='CRITICAL'
        ).count()

        # zone wise matrics
        zones_data = []
        for zone in ParkingZone.objects.all():
            zone_events = ParkingLog.objects.filter(
                device__zone=zone,
                timestamp__range=(start_time, end_time)
            ).count()

            if zone.daily_target > 0:
                efficiancy = (zone_events / zone.daily_target) * 100
            else:
                efficiancy = 0

            zones_data.append({
                'zone_name': zone.name,
                'zone_code': zone.code,
                'events': zone_events,
                'efficiency': round(efficiancy, 2),
                'target': zone.daily_target,
                'status': 'good' if efficiancy >= 80 else 'warning' if efficiancy >= 50 else 'critical'
            })

        return {
            'date': target_data,
            "summary": {
                'total_events': total_events,
                'current_occupancy': current_occupancy,
                'active_devices': active_devices,
                'alerts_today': alerts_today,
                'critical_alerts': critical_alerts,
                'total_devices': Device.objects.count()
            },
            'zones': zones_data,
            'timestamp': timezone.now()
        }
    
class AlertSerializer(serializers.ModelSerializer):
    device_code = serializers.CharField(source='device.device_code', read_only=True)
    zone_name = serializers.CharField(source='device.zone.name', read_only=True)

    class Meta:
        model = Alert
        fields = ['id', 'device_code', 'zone_name', 'severity', 'alert_type', 'message', 'is_acknowledged', 'created_at', 'acknowledged_at']
        read_only_fields = ['created_at', 'acknowledged_at']

class ParkingLogSerializer(serializers.Serializer):
    device_code = serializers.CharField(max_length=50)
    is_occupied = serializers.BooleanField()
    timestamp = serializers.DateTimeField()

    def validate_device_code(self, value):
        try:
            Device.objects.get(device_code=value)
            return value
        except Device.DoesNotExist:
            raise serializers.ValidationError("Device does not exist.")
        
    def validate_timestamp(self, value):
        now = timezone.now()
        if value > now:
            raise serializers.ValidationError("Timestamp cannot be in the future.")
        return value
    
    def create(self, validated_data):
        device = Device.objects.get(device_code=validated_data['device_code'])

        parking_log = ParkingLog.objects.create(
            device=device,
            is_occupied=validated_data['is_occupied'],
            timestamp=validated_data['timestamp']
        )

        return parking_log