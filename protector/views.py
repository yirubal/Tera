from django.shortcuts import render
from rest_framework import  generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from protector.models import Protector
from protector.permissions import IsProtector
from rest_framework.parsers import MultiPartParser, FormParser
from protector.serializers import ProtectorSerializer
from rest_framework.views import APIView
# Create your views here.


class RegisterProtectorView(generics.CreateAPIView):
    queryset = Protector.objects.all()
    serializer_class = ProtectorSerializer
    permission_classes = [IsAuthenticated]  


   


class ProtectorProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProtectorSerializer
    permission_classes = [IsProtector] 
    parser_classes = [MultiPartParser, FormParser]  
    
    def get_object(self):
        # Get the protector profile for the authenticated user
        return self.request.user.protector_profile
    

class ProtectorListView(generics.ListAPIView):
   queryset = Protector.objects.select_related("user").all()
   serializer_class = ProtectorSerializer
   permission_classes = [IsAdminUser]



