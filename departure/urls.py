from django.urls import path
from .views import DeparturesFromHereView, IncomingToHereView, ReceiveDepartureView

urlpatterns = [
    path("from",     DeparturesFromHereView.as_view()),      # GET: list departures from my terminal
    path("incoming", IncomingToHereView.as_view()),          # GET: list incoming to my terminal (unreceived)
    path("<int:pk>/receive", ReceiveDepartureView.as_view()),# POST/PATCH: mark as received
]
