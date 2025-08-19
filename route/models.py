from django.db import models
from terminal.models import Terminal
from django.conf import settings


# Create your models here.

class Route(models.Model):
    from_terminal = models.ForeignKey(Terminal, related_name='from_routes', on_delete=models.CASCADE)
    to_terminal = models.ForeignKey(Terminal, related_name='to_routes', on_delete=models.CASCADE)
    created_by_protector = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_routes', 
                                             on_delete=models.SET_NULL, null=True, blank=True,
                                               )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def clean(self):
        if self.from_terminal == self.to_terminal:
            raise ValueError("A route cannot be from and to the same terminal.")

    class Meta:
        constraints = [
            # one unique directed route A→B
            models.UniqueConstraint(
                fields=["from_terminal", "to_terminal"],
                name="uniq_route_pair",
            ),
            # forbid A→A
            models.CheckConstraint(
                check=~models.Q(from_terminal=models.F("to_terminal")),
                name="route_from_ne_to",
            ),
        ]
        indexes = [
            models.Index(fields=["from_terminal", "to_terminal"]),
        ]

    def __str__(self):
        return f"{self.from_terminal} → {self.to_terminal}"