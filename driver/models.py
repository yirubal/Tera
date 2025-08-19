# driver/models.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Driver(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,           # use project user model safely
        on_delete=models.CASCADE,
        related_name="driver_profile",
        null=True,                          # allow drivers without auth accounts (optional)
        blank=True
    )

   
    phone_number = models.CharField( _("Phone Number"), max_length=32, unique=True, null=True, blank=True,)
    plate_number = models.CharField(max_length=20, unique=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["plate_number"]),
            models.Index(fields=["phone_number"]),
        ]
        verbose_name = _("Driver")
        verbose_name_plural = _("Drivers")

    def save(self, *args, **kwargs):
        # Normalize plate to avoid duplicates with case/spacing differences
        if self.plate_number:
            self.plate_number = self.plate_number.strip().upper()
        # Optional: normalize phone (very light touch if NOT using phonenumber_field)
        if self.phone_number:
            self.phone_number = self.phone_number.strip().replace(" ", "")
        super().save(*args, **kwargs)

    def __str__(self):
        uname = getattr(self.user, "username", None) or "UNLINKED"
        return f"{uname} - {self.plate_number}"
