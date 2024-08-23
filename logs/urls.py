from django.urls import path

from .views import LogEntryList


urlpatterns = [
    path('', LogEntryList.as_view())
]
