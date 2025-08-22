from django.shortcuts import render
from route.serializers import RouteSerializer
from rest_framework import generics, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from protector.permissions import IsProtector
from route.models import Route
# Create your views here.

class RouteListCreateView(generics.ListCreateAPIView):
    serializer_class = RouteSerializer

    def get_queryset(self):
        qs = Route.objects.select_related("from_terminal", "to_terminal").all()
        # optional filters: ?from_terminal=<id>&to_terminal=<id>
        ft = self.request.query_params.get("from_terminal")
        tt = self.request.query_params.get("to_terminal")
        if ft:
            qs = qs.filter(from_terminal_id=ft)
        if tt:
            qs = qs.filter(to_terminal_id=tt)
        return qs.order_by("from_terminal_id", "to_terminal_id")

    def get_permissions(self):
        # anyone can list; must be authenticated to create
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsProtector()]

class RouteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Route.objects.select_related("from_terminal", "to_terminal")
    serializer_class = RouteSerializer
    # require auth to modify; reads are open
    permission_classes = [IsAuthenticated, IsProtector]