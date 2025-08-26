from django.urls import path
from .views import ShiftContextListView, ShiftContextCreateView, ShiftContextDetailView, EndMyShiftView

urlpatterns = [
    path('', ShiftContextListView.as_view(), name='shift-list'),
    path('create/', ShiftContextCreateView.as_view(), name='shift-create'),
    path('end/', EndMyShiftView.as_view(), name='shift-end'),
    path('<int:pk>/', ShiftContextDetailView.as_view(), name='shift-detail'),
]