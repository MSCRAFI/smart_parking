from django.core.management.base import BaseCommand
from monitoring.models import ParkingZone, Device

class Command(BaseCommand):
    help = 'Seed initial data'

    def handle(self, *args, **kwargs):
        zones = [
            {'name': 'Basement-1', 'code': 'B1', 'total_slots': 50, 'daily_target': 200},
            {'name': 'Basement-2', 'code': 'B2', 'total_slots': 40, 'daily_target': 150},
            {'name': 'VIP', 'code': 'VIP', 'total_slots': 20, 'daily_target': 80},
        ]
        
        for zone_data in zones:
            zone, created = ParkingZone.objects.get_or_create(
                code=zone_data['code'],
                defaults=zone_data
            )
            
            if created:
                for i in range(1, 11):  # Create 10 devices per zone
                    Device.objects.create(
                        device_code=f"PARK-{zone.code}-S{i:03d}",
                        zone=zone,
                        slot_number=f"S{i:03d}",
                        is_active=True
                    )
                self.stdout.write(f'Created zone: {zone.name}')
        
        self.stdout.write(self.style.SUCCESS('Data seeded successfully'))