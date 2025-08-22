from rest_framework import serializers
from .models import Terminal



class TerminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terminal
        fields = ['id', 'name']

        