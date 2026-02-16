from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Device, TelemetryData, ParkingZone, ParkingLog, Alert

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