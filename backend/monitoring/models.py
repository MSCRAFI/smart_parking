from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class ParkingZone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    total_slots = models.IntegerField(validators=[MinValueValidator(1)])
    daily_target = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Expected daily parking events",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"
    
class Device(models.Model):
    device_code = models.CharField(max_length=50, unique=True, db_index=True)
    zone = models.ForeignKey(
        ParkingZone,
        on_delete=models.CASCADE,
        related_name='devices'
    )
    slot_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [['zone', 'slot_number']]
        ordering = ['zone', 'slot_number']

    def __str__(self):
        return f"{self.device_code} - Zone: {self.zone.name}"
    
    def update_last_seen(self):
        self.last_seen = timezone.now()
        self.save(update_fields=['last_seen'])

    def is_offline(self):
        if not self.last_seen:
            return True
        return (timezone.now() - self.last_seen).total_seconds() > 120  # offline if last seen more than 2 minutes
    
class TelemetryData(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='telemetry'
    )
    voltage = models.DecimalField(max_digits=6, decimal_places=2)
    current = models.DecimalField(max_digits=6, decimal_places=2)
    power_factor = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    timestamp = models.DateTimeField(db_index=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        unique_together = [['device', 'timestamp']]
        indexes = [
            models.Index(fields=['device', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.device.device_code} - {self.timestamp}"
    
    @property
    def power_consumption(self):
        return float(self.voltage) * float(self.current) * float(self.power_factor)
    
class ParkingLog(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='parking_logs'
    )
    is_occupied = models.BooleanField()
    timestamp = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', '-timestamp']),
            models.Index(fields=['timestamp', 'is_occupied']),
        ]

    def __str__(self):
        if self.is_occupied:
            status = "Occupied"
        else:
            status = "Free"
        return f"{self.device.device_code} - {status} at {self.timestamp}"
    
class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
    ]

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        db_index=True
    )
    alert_type = models.CharField(max_length=50, db_index=True)
    message = models.TextField()
    is_acknowledged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', 'alert_type', 'is_acknowledged']),
            models.Index(fields=['-created_at','severity']),
        ]

    def __str__(self):
        return f"{self.severity} - {self.alert_type} - {self.device.device_code}"
    
    @classmethod
    def create_if_not_exists(cls, device, alert_type, severity, message):
        """Prevent duplicate active alerts"""
        existing = cls.objects.filter(
            device=device,
            alert_type=alert_type,
            is_acknowledged=False
        ).exists()

        if not existing:
            return cls.objects.create(
                device=device,
                alert_type=alert_type,
                severity=severity,
                message=message
            )
        return None