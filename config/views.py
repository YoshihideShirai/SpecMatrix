from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone


def healthcheck(_request):
    return JsonResponse({"status": "ok", "service": "specmatrix"})


def home(request):
    context = {
        "now": timezone.localtime(),
        "release_status": {
            "release": "REL-1.4.0",
            "quality_gate": "未判定",
            "open_high_risk_findings": 3,
            "coverage": 82,
        },
    }
    return render(request, "home.html", context)


def dashboard_summary(request):
    context = {
        "now": timezone.localtime(),
        "release_status": {
            "release": "REL-1.4.0",
            "quality_gate": "レビュー中",
            "open_high_risk_findings": 2,
            "coverage": 86,
        },
    }
    return render(request, "partials/dashboard_summary.html", context)
