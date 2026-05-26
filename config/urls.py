from django.contrib import admin
from django.urls import path

from .views import dashboard_summary, healthcheck, home

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("healthz/", healthcheck, name="healthcheck"),
    path("dashboard/summary/", dashboard_summary, name="dashboard_summary"),
]
