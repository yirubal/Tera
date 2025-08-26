"""
URL configuration for tera project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    # path("api/protectors/", include("protector.urls")),
    # path("api/drivers/", include("driver.urls")),
    # path("api/terminals/", include("terminal.urls")),
    # # path("api/turns/", include("queue.urls")),
    # path("api/departures/", include("departure.urls")),
    # path("api/shift/", include("shift.urls")),
    # path("api/routes/", include("route.urls")),
    # path("api/earnings/", include("earnings.urls")),
    # path("api/analytics/", include("analytics.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/protector/", include("protector.urls")),
    path("api/driver/", include("driver.urls")),
    path("api/terminals/", include("terminal.urls")),
    path("api/route/", include("route.urls")),
    path("api/turns/", include("turns.urls")),
    path("api/shift/", include("shift.urls")),
]
