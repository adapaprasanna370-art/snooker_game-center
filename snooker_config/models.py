
from django.conf import settings
from django.db import models


class SnookerTable(models.Model):
    name = models.CharField(max_length=100, unique=True)
    hourly_rate = models.DecimalField(
    max_digits=8,
    decimal_places=2,
    default=0
)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    table = models.ForeignKey(
        SnookerTable,
        on_delete=models.CASCADE
    )
    booking_date = models.DateField()
    start_time = models.TimeField()
    duration_hours = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(
        max_length=20,
        default="Confirmed"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.username} - {self.table.name}"
