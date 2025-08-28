from django.urls import path
from .views import (
    WaitingTurnCreateView, WaitingTurnListView, MarkDepartedView,
)

urlpatterns = [
    path("", WaitingTurnCreateView.as_view()),          # POST /api/turns
    path("<int:pk>", MarkDepartedView.as_view()),       # PUT  /api/turns/{id}
    path("waiting", WaitingTurnListView.as_view()),     # GET  /api/turns/waiting
         # GET  /api/turns/incoming
]
