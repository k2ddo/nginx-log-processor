from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView

from .models import LogEntry
from .serializers import LogEntrySerializer


class LogEntryList(ListAPIView):
    """List imported log entries with exact filters and text search."""

    queryset = LogEntry.objects.all()
    serializer_class = LogEntrySerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = [
        "ip_address",
        "user",
        "http_method",
        "request_uri",
        "response_code",
        "response_size",
    ]
    search_fields = ["ip_address", "user", "http_method", "request_uri"]
