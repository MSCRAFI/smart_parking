from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
import random
from monitoring.models import ParkingZone, Device, TelemetryData, ParkingLog, Alert

class Command(BaseCommand):
    help = 'Seed comprehensive sample data for dashboard demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--with-history',
            action='store_true',
            help='Generate historical data for the past 7 days',
        )
        parser.add_argument(
            '--with-alerts',
            action='store_true',
            help='Generate sample alerts',
        )

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data seeding...\n')
        
        self.stdout.write('Clearing existing data...')
        Alert.objects.all().delete()
        ParkingLog.objects.all().delete()
        TelemetryData.objects.all().delete()
        Device.objects.all().delete()
        ParkingZone.objects.all().delete()
        
        zones_data = self.create_zones()
        devices = self.create_devices(zones_data)
        
        if kwargs['with_history']:
            self.generate_historical_telemetry(devices)
            self.generate_historical_parking_logs(devices)
        else:
            self.generate_today_telemetry(devices)
            self.generate_today_parking_logs(devices)
        
        if kwargs['with_alerts']:
            self.generate_alerts(devices)
        
        self.stdout.write(self.style.SUCCESS('\n✓ Data seeding completed successfully!'))
        self.print_summary()

    def create_zones(self):
        zones_config = [
            {
                'name': 'Basement-1',
                'code': 'B1',
                'total_slots': 50,
                'daily_target': 200,
            },
            {
                'name': 'Basement-2',
                'code': 'B2',
                'total_slots': 40,
                'daily_target': 150,
            },
            {
                'name': 'Ground Floor',
                'code': 'GF',
                'total_slots': 30,
                'daily_target': 120,
            },
            {
                'name': 'VIP Zone',
                'code': 'VIP',
                'total_slots': 20,
                'daily_target': 80,
            },
            {
                'name': 'Outdoor Lot',
                'code': 'OUT',
                'total_slots': 60,
                'daily_target': 180,
            },
        ]
        
        zones = []
        for zone_data in zones_config:
            zone = ParkingZone.objects.create(**zone_data)
            zones.append(zone)
            self.stdout.write(f'  ✓ Created zone: {zone.name}')
        
        return zones

    def create_devices(self, zones):
        devices = []
        
        for zone in zones:
            for i in range(1, zone.total_slots + 1):
                device = Device.objects.create(
                    device_code=f"PARK-{zone.code}-S{i:03d}",
                    zone=zone,
                    slot_number=f"S{i:03d}",
                    is_active=True,
                    last_seen=timezone.now() - timedelta(seconds=random.randint(0, 300))
                )
                devices.append(device)
        
        self.stdout.write(f'  ✓ Created {len(devices)} devices')
        return devices

    def generate_today_telemetry(self, devices):
        now = timezone.now()
        count = 0
        
        for device in devices:
            num_records = random.randint(5, 15)
            
            for i in range(num_records):
                timestamp = now - timedelta(minutes=random.randint(1, 480))
                
                voltage = round(random.uniform(215.0, 225.0), 2)
                current = round(random.uniform(3.5, 7.5), 2)
                power_factor = round(random.uniform(0.85, 0.98), 2)
                
                if random.random() < 0.05:
                    current = round(random.uniform(15.0, 25.0), 2)
                
                try:
                    TelemetryData.objects.create(
                        device=device,
                        voltage=voltage,
                        current=current,
                        power_factor=power_factor,
                        timestamp=timestamp
                    )
                    count += 1
                except Exception:
                    pass
        
        self.stdout.write(f'  ✓ Created {count} telemetry records for today')

    def generate_historical_telemetry(self, devices):
        now = timezone.now()
        count = 0
        
        for day in range(7):
            day_start = now - timedelta(days=day)
            
            for device in devices:
                for hour in range(24):
                    if random.random() < 0.3:
                        continue
                    
                    timestamp = day_start.replace(
                        hour=hour,
                        minute=random.randint(0, 59),
                        second=random.randint(0, 59)
                    )
                    
                    voltage = round(random.uniform(215.0, 225.0), 2)
                    current = round(random.uniform(3.5, 7.5), 2)
                    power_factor = round(random.uniform(0.85, 0.98), 2)
                    
                    if random.random() < 0.03:
                        current = round(random.uniform(15.0, 25.0), 2)
                    
                    try:
                        TelemetryData.objects.create(
                            device=device,
                            voltage=voltage,
                            current=current,
                            power_factor=power_factor,
                            timestamp=timestamp
                        )
                        count += 1
                    except Exception:
                        pass
        
        self.stdout.write(f'  ✓ Created {count} historical telemetry records')

    def generate_today_parking_logs(self, devices):
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        count = 0
        
        for device in devices:
            current_time = today_start + timedelta(hours=6)
            is_occupied = False
            
            while current_time < now:
                if not is_occupied:
                    ParkingLog.objects.create(
                        device=device,
                        is_occupied=True,
                        timestamp=current_time
                    )
                    is_occupied = True
                    duration = timedelta(minutes=random.randint(30, 240))
                    count += 1
                else:
                    ParkingLog.objects.create(
                        device=device,
                        is_occupied=False,
                        timestamp=current_time
                    )
                    is_occupied = False
                    duration = timedelta(minutes=random.randint(10, 120))
                    count += 1
                
                current_time += duration
            
            if random.random() < 0.6:
                if not is_occupied:
                    ParkingLog.objects.create(
                        device=device,
                        is_occupied=True,
                        timestamp=now - timedelta(minutes=random.randint(5, 60))
                    )
                    count += 1
        
        self.stdout.write(f'  ✓ Created {count} parking logs for today')

    def generate_historical_parking_logs(self, devices):
        now = timezone.now()
        count = 0
        
        for day in range(7):
            day_start = (now - timedelta(days=day)).replace(
                hour=6, minute=0, second=0, microsecond=0
            )
            day_end = day_start + timedelta(hours=16)
            
            for device in devices:
                current_time = day_start
                is_occupied = False
                
                while current_time < day_end:
                    if not is_occupied:
                        ParkingLog.objects.create(
                            device=device,
                            is_occupied=True,
                            timestamp=current_time
                        )
                        is_occupied = True
                        duration = timedelta(minutes=random.randint(30, 240))
                        count += 1
                    else:
                        ParkingLog.objects.create(
                            device=device,
                            is_occupied=False,
                            timestamp=current_time
                        )
                        is_occupied = False
                        duration = timedelta(minutes=random.randint(10, 120))
                        count += 1
                    
                    current_time += duration
        
        self.stdout.write(f'  ✓ Created {count} historical parking logs')

    def generate_alerts(self, devices):
        now = timezone.now()
        count = 0
        
        # Device offline alerts
        offline_devices = random.sample(devices, k=min(5, len(devices)))
        for device in offline_devices:
            device.last_seen = now - timedelta(minutes=random.randint(3, 30))
            device.save()
            
            Alert.objects.create(
                device=device,
                severity='CRITICAL',
                alert_type='DEVICE_OFFLINE',
                message=f'Device has been offline for {(now - device.last_seen).seconds // 60} minutes. Last seen: {device.last_seen.strftime("%Y-%m-%d %H:%M:%S")}',
                is_acknowledged=random.choice([True, False]),
                created_at=device.last_seen + timedelta(minutes=2)
            )
            count += 1
        
        # High power alerts
        high_power_devices = random.sample(devices, k=min(8, len(devices)))
        for device in high_power_devices:
            power_value = round(random.uniform(1500, 2500), 2)
            Alert.objects.create(
                device=device,
                severity='WARNING',
                alert_type='HIGH_POWER',
                message=f'Abnormal power usage: {power_value}W (threshold: 1500W)',
                is_acknowledged=random.choice([True, False]),
                created_at=now - timedelta(hours=random.randint(1, 8))
            )
            count += 1
        
        # Low voltage alerts
        voltage_devices = random.sample(devices, k=min(6, len(devices)))
        for device in voltage_devices:
            voltage = round(random.uniform(200, 210), 2)
            Alert.objects.create(
                device=device,
                severity='WARNING',
                alert_type='LOW_VOLTAGE',
                message=f'Voltage below normal: {voltage}V (expected: 215-225V)',
                is_acknowledged=random.choice([True, False]),
                created_at=now - timedelta(hours=random.randint(2, 12))
            )
            count += 1
        
        # Connection restored
        restored_devices = random.sample(devices, k=min(3, len(devices)))
        for device in restored_devices:
            Alert.objects.create(
                device=device,
                severity='INFO',
                alert_type='CONNECTION_RESTORED',
                message='Device reconnected successfully',
                is_acknowledged=True,
                created_at=now - timedelta(hours=random.randint(1, 6))
            )
            count += 1
        
        # Maintenance required
        maintenance_devices = random.sample(devices, k=min(4, len(devices)))
        for device in maintenance_devices:
            Alert.objects.create(
                device=device,
                severity='WARNING',
                alert_type='MAINTENANCE_REQUIRED',
                message='Device requires maintenance - irregular data patterns detected',
                is_acknowledged=False,
                created_at=now - timedelta(days=random.randint(1, 3))
            )
            count += 1
        
        # Communication timeout
        timeout_devices = random.sample(devices, k=min(3, len(devices)))
        for device in timeout_devices:
            Alert.objects.create(
                device=device,
                severity='CRITICAL',
                alert_type='COMMUNICATION_TIMEOUT',
                message='No response from device for extended period',
                is_acknowledged=False,
                created_at=now - timedelta(hours=random.randint(1, 4))
            )
            count += 1
        
        self.stdout.write(f'  ✓ Created {count} alerts')

    def print_summary(self):
        self.stdout.write('\n' + '='*50)
        self.stdout.write('DATA SUMMARY')
        self.stdout.write('='*50)
        self.stdout.write(f'Parking Zones: {ParkingZone.objects.count()}')
        self.stdout.write(f'Devices: {Device.objects.count()}')
        self.stdout.write(f'Telemetry Records: {TelemetryData.objects.count()}')
        self.stdout.write(f'Parking Logs: {ParkingLog.objects.count()}')
        self.stdout.write(f'Total Alerts: {Alert.objects.count()}')
        self.stdout.write(f'  - Critical: {Alert.objects.filter(severity="CRITICAL").count()}')
        self.stdout.write(f'  - Warning: {Alert.objects.filter(severity="WARNING").count()}')
        self.stdout.write(f'  - Info: {Alert.objects.filter(severity="INFO").count()}')
        self.stdout.write(f'Unacknowledged Alerts: {Alert.objects.filter(is_acknowledged=False).count()}')
        self.stdout.write('='*50 + '\n')