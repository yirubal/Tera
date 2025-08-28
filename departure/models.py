from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from terminal.models import Terminal
from route.models import Route
from driver.models import Driver
from turns.models import WaitingTurn

class DepartureRecord(models.Model):
    class FareMode(models.TextChoices):
        FIXED = "fixed", "Fixed"
        MANUAL = "manual", "Manual"

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    from_terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE, related_name="departures_from")
    to_terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE, related_name="arrivals_to")
    route = models.ForeignKey(Route, on_delete=models.CASCADE)

    departed_at = models.DateTimeField(auto_now_add=True)
    received = models.BooleanField(default=False)
    received_at = models.DateTimeField(null=True, blank=True)

    protector = models.ForeignKey(getattr(settings, "AUTH_USER_MODEL", "auth.User"),
                                  on_delete=models.SET_NULL, null=True, blank=True)
    queue_entry = models.ForeignKey(WaitingTurn, on_delete=models.SET_NULL, null=True, blank=True)
# departure/models.py (Meta)
indexes = [
    models.Index(fields=["from_terminal", "route", "departed_at"]),
    models.Index(fields=["to_terminal", "route", "received"]),
]
