from rest_framework import serializers
from  route.models import Route
from terminal.models import Terminal
from turns.models import WaitingTurn
from driver.models import Driver
from django.db import transaction
from departure.models import DepartureRecord
from django.db.models import Max


class WaitingTurnCreateSerializer(serializers.ModelSerializer):
    plate_number = serializers.CharField(write_only=True)

    class Meta:
        model = WaitingTurn
        fields = ['plate_number']  # Only plate_number is input
        extra_kwargs = {
            'plate_number': {'required': True}
        }

    def validate(self, attrs):
        request = self.context.get("request")
        current_terminal = self.context.get('current_terminal')
        current_route = self.context.get('current_route')  # Add this to context in your view
        plate_number = attrs.get('plate_number')

        if not current_terminal:
            raise serializers.ValidationError("Protector does not have an active shift at any terminal.")

        try:
            driver = Driver.objects.get(plate_number__iexact=plate_number)
        except Driver.DoesNotExist:
            raise serializers.ValidationError("No driver with this plate number exists.")

        
        if current_route.from_terminal != current_terminal:
            raise serializers.ValidationError("The selected route does not start from the current terminal.")

        if WaitingTurn.objects.filter(
            driver=driver,
            terminal=current_terminal,
            status="waiting"
        ).exists():
            raise serializers.ValidationError("This driver already has an active waiting turn at this terminal.")

        attrs['driver'] = driver
        attrs['terminal'] = current_terminal
        attrs['route'] = current_route  
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            current_terminal = validated_data['terminal']
            waiting_qs = WaitingTurn.objects.select_for_update().filter(
                terminal=current_terminal,
                status="waiting"
            )
            last_position = waiting_qs.aggregate(max_pos=Max('position'))['max_pos'] or 0
            waiting_turn = WaitingTurn.objects.create(
                driver=validated_data['driver'],
                terminal=current_terminal,
                route=validated_data['route'],
                position=last_position + 1,
                status="waiting",
                active=True
            )
        return waiting_turn
    
class WaitingTurnSerializer(serializers.ModelSerializer):
    plate_number = serializers.CharField(source="driver.plate_number", read_only=True)
    driver = serializers.PrimaryKeyRelatedField(read_only=True)
    terminal = serializers.StringRelatedField(read_only=True)
    route = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = WaitingTurn
        fields = ["id", "driver", "plate_number", "route", "terminal",
                  "position", "registered_at", "status", "active"]
        read_only_fields = fields


class DepartureMiniSerializer(serializers.ModelSerializer):
    plate_number = serializers.CharField(source='driver.plate_number', read_only=True)
    driver = serializers.PrimaryKeyRelatedField(read_only=True)
    route = serializers.PrimaryKeyRelatedField(read_only=True)
    from_terminal = serializers.StringRelatedField(read_only=True)
    to_terminal = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DepartureRecord
        fields = [
            'id',
            'driver',
            'plate_number',
            'route',
            'from_terminal',
            'to_terminal',
            'departed_at',
            'received',
        ]
        read_only_fields = fields
        



       