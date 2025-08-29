from rest_framework import serializers
from django.utils import timezone
from .models import DepartureRecord

class DepartureMiniSerializer(serializers.ModelSerializer):
    plate_number = serializers.CharField(source='driver.plate_number', read_only=True)
    from_terminal = serializers.StringRelatedField(read_only=True)
    to_terminal = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DepartureRecord
        fields = [
            "id",
            "plate_number",
            "route",
            "from_terminal",
            "to_terminal",
            "departed_at",
            "received",
            "received_at",
        ]
        read_only_fields = fields


class ReceiveDepartureSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DepartureRecord
        fields = []  

    def update(self, instance, validated_data):
        if instance.received:
            raise serializers.ValidationError("Already received.")
        instance.received = True
        instance.received_at = timezone.now()
        instance.save(update_fields=["received", "received_at"])
        return instance
