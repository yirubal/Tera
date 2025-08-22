from rest_framework import serializers
from protector.models import Protector
from django.contrib.auth import get_user_model

User = get_user_model()

class ProtectorSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    # Read-only User info
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name  = serializers.CharField(source="user.last_name",  read_only=True)
    email      = serializers.EmailField(source="user.email",     read_only=True)

    class Meta:
        model = Protector
        fields = ["id", "user", "first_name", "last_name", "email",
                  "phone_number", "profile_picture", "created_at"]
        read_only_fields = ["id", "created_at", "first_name", "last_name", "email"]  # <-- explicit

    def create(self, validated_data):
        user = validated_data["user"]
        if Protector.objects.filter(user=user).exists():
            raise serializers.ValidationError("You already have a protector profile.")
        pn = validated_data.get("phone_number")
        if pn:
            validated_data["phone_number"] = pn.strip().replace(" ", "")
        return Protector.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("user", None)  # never allow switching users
        if "phone_number" in validated_data:
            phone = (validated_data["phone_number"] or "").strip().replace(" ", "")
            instance.phone_number = phone or None
        if "profile_picture" in validated_data:
            instance.profile_picture = validated_data["profile_picture"]
        instance.save()
        return instance
