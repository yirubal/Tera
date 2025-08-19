from django.db import models

# Create your models here.
# shift/models.py (add this next to ShiftContext)
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from terminal.models import Terminal
from shift.models import ShiftContext
from route.models import Route

class ShiftTransfer(models.Model):
    from_shift = models.ForeignKey(ShiftContext, on_delete=models.PROTECT, related_name="transfers_out")
    to_shift   = models.ForeignKey(ShiftContext, on_delete=models.PROTECT, related_name="transfers_in")

    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)
    route    = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)

    from_protector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="shift_transfers_out")
    to_protector   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="shift_transfers_in")

    transfer_at = models.DateTimeField(default=timezone.now)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(from_protector=models.F("to_protector")),
                name="shift_transfer_different_users",
            ),
            models.UniqueConstraint(fields=["from_shift"], name="one_transfer_per_from_shift"),
            models.UniqueConstraint(fields=["to_shift"], name="one_transfer_per_to_shift"),
        ]
        indexes = [
            models.Index(fields=["terminal", "transfer_at"]),
            models.Index(fields=["from_protector", "transfer_at"]),
            models.Index(fields=["to_protector", "transfer_at"]),
        ]

    def clean(self):
        # sanity: same terminal, matching time
        if self.from_shift.terminal_id != self.terminal_id or self.to_shift.terminal_id != self.terminal_id:
            raise ValidationError("Transfer terminal must match both shifts.")
        if self.route_id and (self.from_shift.route_id != self.route_id or self.to_shift.route_id != self.route_id):
            raise ValidationError("Transfer route must match both shifts (when provided).")
