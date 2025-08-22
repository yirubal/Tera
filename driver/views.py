from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework import  generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework.parsers import MultiPartParser, FormParser
from driver.permissions import IsDriver
from driver.serializers import DriverSerializer
from driver.models import Driver
from rest_framework.views import APIView
# Create your views here.


class RegisterDriverView(generics.CreateAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated to register a protector profile


   


class DriverProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DriverSerializer
    permission_classes = [IsDriver] 
    parser_classes = [MultiPartParser, FormParser]  # allow image upload
    
    def get_object(self):
        # Get the protector profile for the authenticated user
        return self.request.user.driver_profile
    

class DriverListView(generics.ListAPIView):
   queryset = Driver.objects.select_related("user").all()
   serializer_class = DriverSerializer
   permission_classes = [IsAdminUser]



