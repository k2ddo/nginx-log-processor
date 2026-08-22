import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from django.urls import reverse
from unfold.admin import ModelAdmin

from logs.models import LogEntry


@pytest.mark.django_db
def test_unfold_admin_pages_render(client, settings):
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    user = get_user_model().objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="secret",
    )
    client.force_login(user)

    index_response = client.get(reverse("admin:index"))
    logs_response = client.get(reverse("admin:logs_logentry_changelist"))

    assert index_response.status_code == 200
    assert logs_response.status_code == 200
    assert b"Nginx Log Processor" in index_response.content


@pytest.mark.parametrize("model", [LogEntry, User, Group])
def test_registered_admins_use_unfold(model):
    assert isinstance(admin.site._registry[model], ModelAdmin)
