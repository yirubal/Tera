from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from django.db import transaction
from django.db.models import Min
from route.models import Route
from shift.models import ShiftContext
from .models import WaitingTurn
from .serializers import WaitingTurnCreateSerializer, WaitingTurnSerializer, DepartureMiniSerializer
from shift.models import ShiftContext
from departure.models import DepartureRecord
from protector.permissions import IsProtector

# # def get_current_terminal(user):
# #     """Active terminal for the logged-in protector."""
# #     s = (ShiftContext.objects
# #          .select_related("terminal")
# #          .filter(protector=user, end_time__isnull=True)
# #          .first())
# #     return s.terminal if s else None

# def get_current_route_for_terminal(terminal):
#     """Return the active route for the given terminal."""
#     if not terminal:
#         return None
#     # Example: get the first route starting from this terminal
#     return Route.objects.filter(from_terminal=terminal).first()



def get_current_shift(user):
    return (ShiftContext.objects
            .select_related("terminal", "route")
            .filter(protector=user, end_time__isnull=True)
            .first())



# POST /api/turns
class WaitingTurnCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsProtector]
    serializer_class = WaitingTurnCreateSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        shift = get_current_shift(self.request.user)
        ctx["current_terminal"] = shift.terminal if shift else None
        ctx["current_route"]    = shift.route if shift else None  # ← selected route for this shift
        return ctx

# GET /api/turns/waiting
# turns/views.py

class WaitingTurnListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsProtector]
    serializer_class = WaitingTurnSerializer

    def get_queryset(self):
        shift = get_current_shift(self.request.user)  # must include .select_related("terminal","route")
        if not shift or not shift.terminal:
            raise ValidationError("You don't have an active shift.")
        if not shift.route:
            raise ValidationError("Set a route for your active shift to view its queue.")

        return (WaitingTurn.objects
                .filter(
                    terminal=shift.terminal,
                    route=shift.route,          # ← key change: scope to this protector’s route
                    status="waiting",
                )
                .order_by("position", "registered_at"))


# turns/views.py

class MarkDepartedView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsProtector]
    serializer_class = DepartureMiniSerializer

    queryset = WaitingTurn.objects.all()
    def put(self, request, pk:int):
        shift = get_current_shift(self.request.user)
        if not shift or not shift.terminal:
            raise ValidationError("You don't have an active shift.")
        if not shift.route:
            raise ValidationError("Set a route for your active shift before departing a driver.")

        term  = shift.terminal
        route = shift.route

        with transaction.atomic():
            waiting_qs = (WaitingTurn.objects
                          .select_for_update()
                          .filter(terminal=term, route=route, status="waiting"))  # ← include route

            wt = waiting_qs.filter(pk=pk).select_related("driver", "route").first()
            if not wt:
                raise NotFound("Waiting turn not found in your route queue.")

            head_pos = waiting_qs.aggregate(m=Min("position"))["m"]
            if wt.position != head_pos:
                raise ValidationError("Only the first in your route queue can depart.")

            dep = DepartureRecord.objects.create(
                driver=wt.driver,
                from_terminal=term,
                to_terminal=route.to_terminal,
                route=route,
                protector=request.user,
                queue_entry=wt,
            )
            wt.status = "done"
            wt.active = False
            wt.save(update_fields=["status", "active"])

        return Response(DepartureMiniSerializer(dep).data, status=status.HTTP_200_OK)
