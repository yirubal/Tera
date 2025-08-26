from rest_framework import serializers
from shift.models import ShiftContext
from terminal.models import Terminal
from route.models import Route
from django.db import transaction, IntegrityError 
from django.utils import timezone

class ShiftContextSerializer(serializers.ModelSerializer):
    protector = serializers.HiddenField(default=serializers.CurrentUserDefault())
    terminal  = serializers.PrimaryKeyRelatedField(queryset=Terminal.objects.all())
    route     = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all(), required=False, allow_null=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = ShiftContext
        fields = ["id", "protector",  "terminal", "route", "is_active"]
        read_only_fields = ["id", "start_time", "end_time", "is_active"]
        

    def get_is_active(self, obj):
        return obj.end_time is None

    def validate(self, attrs):
        user     = self.context['request'].user
        terminal = attrs.get('terminal', getattr(self.instance, 'terminal', None))
        route    = attrs.get('route',    getattr(self.instance, 'route',    None))

    
        if route and terminal and route.from_terminal_id != terminal.id:
            raise serializers.ValidationError("Selected route must start at the selected terminal.")

      
        if self.instance is None:
            if ShiftContext.objects.filter(protector=user, end_time__isnull=True).exists():
                raise serializers.ValidationError("You already have an active shift. End or transfer it first.")
            if terminal and ShiftContext.objects.filter(terminal=terminal, end_time__isnull=True).exists():
                raise serializers.ValidationError("This terminal already has an active shift.")

        return attrs

    def create(self, validated_data):
      
        try:
            with transaction.atomic():
                return ShiftContext.objects.create(**validated_data)
        except IntegrityError:
          
            raise serializers.ValidationError("Active shift already exists for this protector or terminal.")

    def update(self, instance, validated_data):
    
        validated_data.pop('protector', None)

        
        if 'terminal' in validated_data:
            raise serializers.ValidationError("You cannot change the terminal of an existing shift. End and start a new one.")

        return super().update(instance, validated_data)
