from datetime import UTC, datetime

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from logs.models import LogEntry


@pytest.fixture
def api_client(db):
    user = get_user_model().objects.create_user(username="reader", password="secret")
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def log_entries(db):
    return LogEntry.objects.bulk_create(
        [
            LogEntry(
                date=datetime(2024, 1, 1, tzinfo=UTC),
                ip_address="192.0.2.1",
                user="alice",
                http_method="GET",
                request_uri="/downloads/one",
                response_code=200,
                response_size=100,
            ),
            LogEntry(
                date=datetime(2024, 1, 2, tzinfo=UTC),
                ip_address="192.0.2.2",
                user="bob",
                http_method="POST",
                request_uri="/uploads/two",
                response_code=201,
                response_size=200,
            ),
        ]
    )


@pytest.mark.django_db
def test_log_list_requires_authentication():
    response = APIClient().get(reverse("log-entry-list"))

    assert response.status_code == 403


def test_log_list_is_paginated_and_ordered(api_client, log_entries):
    response = api_client.get(reverse("log-entry-list"))

    assert response.status_code == 200
    assert response.data["count"] == 2
    assert response.data["results"][0]["id"] == log_entries[1].id


def test_log_list_supports_exact_filters(api_client, log_entries):
    response = api_client.get(reverse("log-entry-list"), {"response_code": 200})

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["user"] == "alice"


def test_log_list_supports_text_search(api_client, log_entries):
    response = api_client.get(reverse("log-entry-list"), {"search": "uploads"})

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["http_method"] == "POST"


@pytest.mark.django_db
def test_health_and_schema_endpoints_are_public():
    client = APIClient()

    health_response = client.get(reverse("health"))
    schema_response = client.get(reverse("schema"))

    assert health_response.json() == {"status": "ok"}
    assert schema_response.status_code == 200
