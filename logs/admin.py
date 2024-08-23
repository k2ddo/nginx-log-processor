from django.contrib import admin

from .models import LogEntry


class Filter(admin.ModelAdmin):
    list_display = ['date', 'http_method', 'request_uri', 'response_code',]
    list_filter = ['http_method', 'request_uri', 'response_code',]


admin.site.register(LogEntry, Filter)
