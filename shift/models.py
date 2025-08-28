# shift/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

from terminal.models import Terminal
from route.models import Route

class ShiftContext(models.Model):
    protector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shifts",
    )
   
    terminal = models.ForeignKey(
        Terminal,
        on_delete=models.CASCADE,
        related_name="shifts",
    )
   
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="shifts",
        null=True,
        blank=True,
    )

    start_time = models.DateTimeField(default=timezone.now)  # start = now by default
    end_time   = models.DateTimeField(null=True, blank=True) # NULL means "active"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        
        constraints = [
             models.UniqueConstraint(
        fields=["protector"],
        condition=models.Q(end_time__isnull=True),
        name="one_active_shift_per_protector",
    ),
    # NEW: one active shift per (terminal, route)
    models.UniqueConstraint(
        fields=["terminal", "route"],
        condition=models.Q(end_time__isnull=True),
        name="one_active_shift_per_terminal_route",
    ),
        ]
        indexes = [
            models.Index(fields=["terminal", "end_time"]),
            models.Index(fields=["protector", "end_time"]),
        ]

    def clean(self):
      
        if self.route and self.route.from_terminal_id != self.terminal_id:
            raise ValidationError("Selected route must start at the shift's terminal.")

    def save(self, *args, **kwargs):
        #
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_active(self) -> bool:
        return self.end_time is None

    def __str__(self):
        route_label = f" | {self.route}" if self.route_id else ""
        end = self.end_time.strftime("%Y-%m-%d %H:%M") if self.end_time else "active"
        return f"{self.protector} @ {self.terminal}{route_label} [{self.start_time:%Y-%m-%d %H:%M} → {end}]"
