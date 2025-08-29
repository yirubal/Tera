from django.shortcuts import render
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from protector.permissions import IsProtector
from terminal.models import Terminal
from terminal.serializers import TerminalSerializer
# Create your views here.


class TerminalView(generics.ListAPIView):
    queryset = Terminal.objects.all()
    serializer_class = TerminalSerializer
    permission_classes = [AllowAny]  
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']  
    ordering_fields = ['name', 'created_at']

class TerminalCreateView(generics.CreateAPIView):
    queryset = Terminal.objects.all()
    serializer_class = TerminalSerializer
    permission_classes = [IsAuthenticated, IsProtector]  # Only admin users can create terminals

class TerminalDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Terminal.objects.all()
    serializer_class = TerminalSerializer
    permission_classes = [IsAuthenticated, IsProtector]  # Only admin users can update or delete terminals