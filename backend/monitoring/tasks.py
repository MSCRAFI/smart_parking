from django.utils import timezone
from datetime import timedelta
from .models import Alert, Device

def check_offline_devices():
    """Background task to check for offline devices"""
    threshold = timezone.now() - timedelta(minutes=2)

    offline_devices = Device.objects.filter(
        is_active=True,
        last_seen__lt=threshold
    )

    for device in offline_devices:
        Alert.create_if_not_exists(
            device=device,
            alert_type="DEVICE_OFFLINE",
            severity="CRITICAL",
            message=f"Device {device.device_code} has been offline for more than 2 minutes. Last seen: {device.last_seen}"
        )