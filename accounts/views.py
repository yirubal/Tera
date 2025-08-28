from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import SignupSerializer

class SignupView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignupSerializer
