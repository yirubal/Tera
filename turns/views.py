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
class WaitingTurnListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsProtector]
    serializer_class = WaitingTurnSerializer

    def get_queryset(self):
        shift = get_current_shift(self.request.user)
        term = shift.terminal if shift else None
        if not term:
            raise ValidationError("You don't have an active shift.")
        return (WaitingTurn.objects
                .filter(terminal=term, status="waiting")
                .order_by("position", "registered_at"))

# PUT /api/turns/{id}
class MarkDepartedView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsProtector]

    def put(self, request, pk:int):
        shift = get_current_shift(self.request.user)
        term = shift.terminal if shift else None
        if not term:
            raise ValidationError("You don't have an active shift.")

        with transaction.atomic():
            # lock all waiting rows at this terminal to prevent race
            waiting_qs = (WaitingTurn.objects
                          .select_for_update()
                          .filter(terminal=term, status="waiting"))

            wt = waiting_qs.filter(pk=pk).select_related("driver", "route").first()
            if not wt:
                raise NotFound("Waiting turn not found at your terminal.")

            # Enforce FIFO: only the head can depart
            head_pos = waiting_qs.aggregate(m=Min("position"))["m"]
            if wt.position != head_pos:
                raise ValidationError("Only the first in the queue can depart.")

            # Create departure
            dep = DepartureRecord.objects.create(
                driver=wt.driver,
                from_terminal=term,
                to_terminal=wt.route.to_terminal,
                route=wt.route,
                protector=request.user,
                queue_entry=wt,
            )
            # Close waiting row
            wt.status = "done"
            wt.active = False
            wt.save(update_fields=["status", "active"])

        return Response(DepartureMiniSerializer(dep).data, status=status.HTTP_200_OK)

# GET /api/turns/departed
class DepartedListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsProtector]
    serializer_class = DepartureMiniSerializer

    def get_queryset(self):
        shift  = get_current_shift(self.request.user)
        term = shift.terminal if shift else None
        if not term:
            raise ValidationError("You don't have an active shift.")
        return (DepartureRecord.objects
                .select_related("driver", "route", "from_terminal", "to_terminal")
                .filter(from_terminal=term, received=False)
                .order_by("-departed_at"))

# GET /api/turns/incoming
class IncomingListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsProtector]
    serializer_class = DepartureMiniSerializer

    def get_queryset(self):
        shift = get_current_shift(self.request.user)
        term = shift.terminal if shift else None
        if not term:
            raise ValidationError("You don't have an active shift.")
        return (DepartureRecord.objects
                .select_related("driver", "route", "from_terminal", "to_terminal")
                .filter(to_terminal=term, received=False)
                .order_by("departed_at"))
