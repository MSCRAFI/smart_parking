from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from monitoring.models import Device, Alert

class Command(BaseCommand):
    help = 'Add alerts to existing devices'

    def handle(self, *args, **kwargs):
        devices = list(Device.objects.all())
        
        if not devices:
            self.stdout.write(self.style.ERROR('No devices found. Run seed_data first.'))
            return
        
        now = timezone.now()
        count = 0
        
        # Critical: Device offline
        offline_devices = random.sample(devices, k=min(5, len(devices)))
        for device in offline_devices:
            device.last_seen = now - timedelta(minutes=random.randint(3, 30))
            device.save()
            
            Alert.objects.create(
                device=device,
                severity='CRITICAL',
                alert_type='DEVICE_OFFLINE',
                message=f'Device offline for {(now - device.last_seen).seconds // 60} minutes',
                is_acknowledged=False
            )
            count += 1
        
        # Warning: High power
        high_power_devices = random.sample(devices, k=min(8, len(devices)))
        for device in high_power_devices:
            power = round(random.uniform(1500, 2500), 2)
            Alert.objects.create(
                device=device,
                severity='WARNING',
                alert_type='HIGH_POWER',
                message=f'Abnormal power usage: {power}W (threshold: 1500W)',
                is_acknowledged=False
            )
            count += 1
        
        # Warning: Low voltage
        voltage_devices = random.sample(devices, k=min(6, len(devices)))
        for device in voltage_devices:
            voltage = round(random.uniform(200, 210), 2)
            Alert.objects.create(
                device=device,
                severity='WARNING',
                alert_type='LOW_VOLTAGE',
                message=f'Voltage below normal: {voltage}V (expected: 215-225V)',
                is_acknowledged=False
            )
            count += 1
        
        # Critical: Communication timeout
        timeout_devices = random.sample(devices, k=min(3, len(devices)))
        for device in timeout_devices:
            Alert.objects.create(
                device=device,
                severity='CRITICAL',
                alert_type='COMMUNICATION_TIMEOUT',
                message='No response from device for extended period',
                is_acknowledged=False
            )
            count += 1
        
        # Info: Connection restored
        restored_devices = random.sample(devices, k=min(3, len(devices)))
        for device in restored_devices:
            Alert.objects.create(
                device=device,
                severity='INFO',
                alert_type='CONNECTION_RESTORED',
                message='Device reconnected successfully',
                is_acknowledged=True
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {count} alerts'))
        self.stdout.write(f'Total alerts in system: {Alert.objects.count()}')
        self.stdout.write(f'Unacknowledged: {Alert.objects.filter(is_acknowledged=False).count()}')