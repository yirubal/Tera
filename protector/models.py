# protector/models.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Protector(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="protector_profile",
        null=True,   # set to False if every protector MUST have a login
        blank=True,
    )

    phone_number = models.CharField(
        _("Phone Number"),
        max_length=32,
        unique=True,          # keep if you want one unique phone per protector
        null=True,
        blank=True,
    )

    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),          # useful for joins
            models.Index(fields=["phone_number"]),  # speeds exact/like lookups
        ]
        verbose_name = _("Protector")
        verbose_name_plural = _("Protectors")

    def save(self, *args, **kwargs):
        if self.phone_number:
            self.phone_number = self.phone_number.strip().replace(" ", "")
        super().save(*args, **kwargs)

    def __str__(self):
        u = self.user
        # Prefer full name; fall back to username; handle null user safely
        label = (u.get_full_name() or u.username) if u else "UNLINKED"
        return f"{label}"
