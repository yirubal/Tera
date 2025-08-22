from django.urls import path
from .views import RouteListCreateView, RouteDetailView

urlpatterns = [
    path("", RouteListCreateView.as_view()),          # GET list, POST create
    path("<int:pk>/", RouteDetailView.as_view()),     # GET one, PATCH/PUT, DELETE
]