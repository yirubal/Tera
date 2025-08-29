from django.urls import path 
from .views import RegisterProtectorView, ProtectorProfileView, ProtectorListView

urlpatterns = [
    path("register", RegisterProtectorView.as_view()),
    path("me",       ProtectorProfileView.as_view()),
    path("list",     ProtectorListView.as_view()), 
]

