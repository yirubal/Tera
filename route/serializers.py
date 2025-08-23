from rest_framework import serializers
from  route.models import Route
from terminal.models import Terminal

class RouteSerializer(serializers.ModelSerializer):
    from_terminal = serializers.SlugRelatedField(queryset = Terminal.objects.all(), slug_field="name")
    to_terminal = serializers.SlugRelatedField(queryset = Terminal.objects.all(), slug_field="name")

    created_by_protector = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Route
        fields = ['id', 'from_terminal', 'to_terminal', 'created_by_protector', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


    def validate(self, attrs):
        # A must not equal B (give a clean 400 instead of DB error)
        if attrs["from_terminal"] == attrs["to_terminal"]:
            raise serializers.ValidationError("from_terminal and to_terminal must be different.")
        # friendly duplicate check (A→B unique)
        qs = Route.objects.filter(
            from_terminal=attrs["from_terminal"],
            to_terminal=attrs["to_terminal"],
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("This route already exists (same from→to).")
        return attrs

    def update(self, instance, validated_data):
        # never allow swapping the creator on update
        validated_data.pop("created_by_protector", None)
        return super().update(instance, validated_data)