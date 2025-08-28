from django.db import models

# Create your models here.
from django.db import models
from terminal.models import Terminal
from route.models import Route
from driver.models import Driver

class WaitingTurn(models.Model):
    class Status(models.TextChoices):
        WAITING = "waiting", "Waiting"
        ACTIVE = "active", "Active"
        DONE = "done", "Done"
        CANCELED = "canceled", "Canceled"
        SKIPPED = "skipped", "Skipped"



    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)  # direction matters
    registered_at = models.DateTimeField(auto_now_add=True)
    position = models.PositiveIntegerField(default=0)       # server-managed
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.WAITING)
    active = models.BooleanField(default=True)




    class Meta:
        ordering = ["position", "registered_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["driver", "terminal", "active"],
                condition=models.Q(active=True),
                name="one_active_waiting_per_driver_terminal",
            ),
        ]

indexes = [
    models.Index(fields=["terminal", "route", "status", "position"]),
]
