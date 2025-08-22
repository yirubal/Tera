from rest_framework import serializers
from driver.models import Driver
from protector.models import Protector

from django.contrib.auth import get_user_model

User = get_user_model()

class DriverSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    # Read-only User info
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name  = serializers.CharField(source="user.last_name",  read_only=True)
    email      = serializers.EmailField(source="user.email",     read_only=True)

    class Meta:
        model = Driver
        fields = ["id", "user", "first_name", "last_name", "email",
                  "phone_number", "plate_number", "profile_picture", "created_at"]
        read_only_fields = ["id", "created_at", "first_name", "last_name", "email"]  # <-- explicit

    def create(self, validated_data):
        user = validated_data["user"]
        if Driver.objects.filter(user=user).exists():
            raise serializers.ValidationError("You already have a driver profile.")
        
        if Protector.objects.filter(user=user).exists():
            raise serializers.ValidationError("You already have a protector profile. You cannot register as a driver.")
        
        pn = validated_data.get("phone_number")
        plate_number = validated_data.get("plate_number")

        if plate_number:
            validated_data["plate_number"] = plate_number.strip().replace(" ", "")
        if pn:
            validated_data["phone_number"] = pn.strip().replace(" ", "")
        return Driver.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("user", None)  # never allow switching users

        if "plate_number" in validated_data:
            plate_number = (validated_data["plate_number"] or "").strip().replace(" ", "")
            instance.plate_number = plate_number or None

        if "phone_number" in validated_data:
            phone = (validated_data["phone_number"] or "").strip().replace(" ", "")
            instance.phone_number = phone or None

        if "profile_picture" in validated_data:
            instance.profile_picture = validated_data["profile_picture"]

        instance.save()
        return instance
