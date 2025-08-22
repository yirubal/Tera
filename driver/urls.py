from django.urls import path

from .views import RegisterDriverView, DriverProfileView, DriverListView

urlpatterns = [
    path("register", RegisterDriverView.as_view()),
    path("me",       DriverProfileView.as_view()),
    path("list",     DriverListView.as_view()),   # optional/admin
]