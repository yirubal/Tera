from django.urls import path
from .views import (
    WaitingTurnCreateView, WaitingTurnListView, MarkDepartedView,
    DepartedListView, IncomingListView
)

urlpatterns = [
    path("", WaitingTurnCreateView.as_view()),          # POST /api/turns
    path("<int:pk>", MarkDepartedView.as_view()),       # PUT  /api/turns/{id}
    path("waiting", WaitingTurnListView.as_view()),     # GET  /api/turns/waiting
    path("departed", DepartedListView.as_view()),       # GET  /api/turns/departed
    path("incoming", IncomingListView.as_view()),       # GET  /api/turns/incoming
]
