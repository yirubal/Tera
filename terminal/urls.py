from django.urls import path
from terminal.views import TerminalView, TerminalCreateView, TerminalDetailView
urlpatterns = [
    path('', TerminalView.as_view(), name='terminal-list'),
    path('create/', TerminalCreateView.as_view(), name='terminal-create'),
    path('<int:pk>/', TerminalDetailView.as_view(), name='terminal-detail'),
]
