"""Root URL configuration."""

from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView


def health_check(_request):
    """Return a lightweight liveness response for orchestrators."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health_check, name="health"),
    path("admin/", admin.site.urls),
    path("api/logs/", include("logs.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
]

if settings.ENABLE_API_DOCS:
    from drf_spectacular.views import SpectacularRedocView, SpectacularSwaggerView

    urlpatterns += [
        path(
            "api/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
        path(
            "api/schema/swagger/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger",
        ),
    ]
