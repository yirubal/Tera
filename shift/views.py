from django.shortcuts import render
from rest_framework import generics, permissions
from protector.permissions import IsProtector
from shift.models import ShiftContext
from shift.serializers import ShiftContextSerializer  
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.utils import timezone
# Create your views here.

class ShiftContextListView(generics.ListAPIView):
    serializer_class = ShiftContextSerializer
    permission_classes = [permissions.IsAuthenticated, IsProtector]

    def get_queryset(self):
        qs = (ShiftContext.objects
              .filter(protector=self.request.user)
              .select_related("terminal", "route")
              .order_by("-start_time"))  # newest first

        status_q = self.request.query_params.get("active")
        if status_q == "true":
            qs = qs.filter(end_time__isnull=True)
        elif status_q == "false":
            qs = qs.filter(end_time__isnull=False)

        # optional filters:
        term = self.request.query_params.get("terminal_id")
        if term: qs = qs.filter(terminal_id=term)
        route = self.request.query_params.get("route_id")
        if route: qs = qs.filter(route_id=route)

        return qs

class ShiftContextCreateView(generics.CreateAPIView):
    serializer_class = ShiftContextSerializer
    permission_classes = [permissions.IsAuthenticated, IsProtector]

    def perform_create(self, serializer):
        serializer.save(protector=self.request.user)

class ShiftContextDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShiftContextSerializer
    permission_classes = [permissions.IsAuthenticated, IsProtector]
    queryset = ShiftContext.objects.all()

    def get_queryset(self):
        return ShiftContext.objects.filter(protector=self.request.user)
    

class EndMyShiftView(generics.UpdateAPIView):
    serializer_class = ShiftContextSerializer  # or a tiny EndShiftSerializer
    permission_classes = [permissions.IsAuthenticated, IsProtector]

    def get_object(self):
        obj = ShiftContext.objects.filter(protector=self.request.user, end_time__isnull=True).first()
        if not obj:
            raise NotFound("No active shift to end.")
        return obj

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.end_time = timezone.now()
        obj.save(update_fields=["end_time", "updated_at"])
        return Response({"ended_at": obj.end_time})
    

class ActiveShiftView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, IsProtector]
    serializer_class = ShiftContextSerializer
    def get_object(self):
        return ShiftContext.objects.select_related("terminal","route")\
               .get(protector=self.request.user, end_time__isnull=True)
