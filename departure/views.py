from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from django.utils import timezone
from route.models import Route

from .models import DepartureRecord
from .serializers import DepartureMiniSerializer, ReceiveDepartureSerializer
from shift.models import ShiftContext

# Helper: find my active terminal
def get_current_terminal(user):
    s = (ShiftContext.objects
         .select_related("terminal")
         .filter(protector=user, end_time__isnull=True)
         .first())
    return s.terminal if s else None

def get_current_shift(user):
    
    return (
        ShiftContext.objects
        .select_related("terminal", "route")
        .filter(protector=user, end_time__isnull=True)
        .first()
    )

# departure/views.py
class DeparturesFromHereView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DepartureMiniSerializer

    def get_queryset(self):
        shift = get_current_shift(self.request.user)  # make sure this returns terminal+route
        if not shift or not shift.terminal:
            raise ValidationError("You don't have an active shift.")
        if not shift.route:
            raise ValidationError("Set a route for your active shift to view departures.")

        term  = shift.terminal
        route = shift.route

        qs = (DepartureRecord.objects
              .select_related("driver", "route", "from_terminal", "to_terminal")
              .filter(from_terminal=term, route=route)   
              .order_by("-departed_at"))

        rec = self.request.query_params.get("received")
        if rec == "true":
            qs = qs.filter(received=True)
        elif rec == "false":
            qs = qs.filter(received=False)
        return qs





def get_reverse_route(route):
    # reverse means: route.to → route.from
    return Route.objects.filter(
        from_terminal=route.to_terminal,
        to_terminal=route.from_terminal
    ).first()

class IncomingToHereView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DepartureMiniSerializer

    def get_queryset(self):
        shift = get_current_shift(self.request.user)
        if not shift or not shift.terminal:
            raise ValidationError("You don't have an active shift.")
        if not shift.route:
            raise ValidationError("Set a route for your active shift to view incoming.")

        term           = shift.terminal
        reverse_route  = get_reverse_route(shift.route)
        if not reverse_route:
            # If you haven’t created the reverse route, nothing to receive for this lane
            return DepartureRecord.objects.none()

        return (DepartureRecord.objects
                .select_related("driver", "route", "from_terminal", "to_terminal")
                .filter(to_terminal=term, route=reverse_route, received=False)  # ← only my reverse lane
                .order_by("departed_at"))


# POST /api/departure/{id}/receive
class ReceiveDepartureView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReceiveDepartureSerializer
    queryset = DepartureRecord.objects.all()

    def get_object(self):
        obj = super().get_object()
        term = get_current_terminal(self.request.user)
        if not term:
            raise ValidationError("You don't have an active shift.")
        if obj.to_terminal_id != term.id:
            # don’t let someone at another terminal receive it
            raise ValidationError("This departure is not incoming to your terminal.")
        if obj.received:
            raise ValidationError("Already received.")
        return obj

    def update(self, request, *args, **kwargs):
        # call serializer.update() (marks received + timestamp)
        return super().update(request, *args, **kwargs)
