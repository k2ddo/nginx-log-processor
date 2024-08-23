from rest_framework.serializers import ModelSerializer

from .models import LogEntry


class LogEntrySerializer(ModelSerializer):
    class Meta:
        model = LogEntry
        fields = (
            'date',
            'ip_address',
            'user',
            'http_method',
            'request_uri',
            'response_code',
            'response_size',
        )
