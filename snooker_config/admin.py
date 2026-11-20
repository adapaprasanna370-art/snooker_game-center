
from django.contrib import admin
from .models import SnookerTable, Booking


@admin.register(SnookerTable)
class SnookerTableAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "hourly_rate", "is_active")
    list_editable = ("hourly_rate", "is_active")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "player",
        "table",
        "booking_date",
        "start_time",
        "duration_hours",
        "status",
    )
    list_filter = ("booking_date", "status", "table")
    search_fields = ("player__username",)
