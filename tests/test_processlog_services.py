from datetime import UTC, datetime
from io import BytesIO
from unittest.mock import Mock, patch

import ijson
import pytest
import requests

from logs.management.commands._processlog_services import (
    DOWNLOAD_TIMEOUT,
    fetch_log_file,
    parse_and_store_logs,
    parse_date,
    parse_request,
    process_log,
)
from logs.models import LogEntry

LOG_DATA = (
    b'{"time":"17/May/2015:08:05:32 +0000","remote_ip":"192.168.1.1",'
    b'"remote_user":"alice","request":"GET /downloads/1 HTTP/1.1",'
    b'"response":200,"bytes":1024}\n'
    b'{"time":"17/May/2015:08:05:33 +0000","remote_ip":"2001:db8::1",'
    b'"remote_user":"-","request":"POST /downloads/2 HTTP/2",'
    b'"response":404,"bytes":0}\n'
)


@pytest.mark.django_db
def test_parse_and_store_logs_in_batches():
    imported = parse_and_store_logs(BytesIO(LOG_DATA), batch_size=1)

    assert imported == 2
    assert LogEntry.objects.count() == 2
    first = LogEntry.objects.order_by("date").first()
    assert first.ip_address == "192.168.1.1"
    assert first.user == "alice"
    assert first.http_method == "GET"
    assert first.request_uri == "/downloads/1"
    assert first.response_code == 200
    assert first.response_size == 1024


@pytest.mark.django_db
def test_parse_and_store_logs_handles_empty_stream():
    assert parse_and_store_logs(BytesIO(b"")) == 0
    assert LogEntry.objects.count() == 0


def test_parse_and_store_logs_rejects_invalid_batch_size():
    with pytest.raises(ValueError, match="greater than zero"):
        parse_and_store_logs(BytesIO(LOG_DATA), batch_size=0)


def test_parse_and_store_logs_rejects_non_object_records():
    with pytest.raises(ValueError, match="must be a JSON object"):
        parse_and_store_logs(BytesIO(b"[1, 2, 3]"))


@pytest.mark.django_db
def test_parse_and_store_logs_rejects_truncated_input_after_valid_record():
    with pytest.raises(ijson.IncompleteJSONError):
        parse_and_store_logs(BytesIO(b'{"request":"GET / HTTP/1.1"}\n{"request":'))


def test_process_log_normalizes_optional_fields():
    entry = process_log(
        {
            "time": None,
            "remote_ip": None,
            "remote_user": "-",
            "request": None,
            "response": None,
            "bytes": None,
        }
    )

    assert entry.date is None
    assert entry.user == ""
    assert entry.http_method == ""
    assert entry.request_uri == ""


def test_parse_date():
    assert parse_date("17/May/2015:08:05:32 +0000") == datetime(2015, 5, 17, 8, 5, 32, tzinfo=UTC)
    assert parse_date(None) is None


@pytest.mark.parametrize(
    ("raw_request", "expected"),
    [
        ("GET / HTTP/1.1", ("GET", "/")),
        ("BROKEN", (None, None)),
        (None, (None, None)),
    ],
)
def test_parse_request(raw_request, expected):
    assert parse_request(raw_request) == expected


def test_fetch_log_file_opens_stream_with_limits():
    response = Mock()
    with patch("requests.get", return_value=response) as request:
        assert fetch_log_file("https://example.com/access.log") is response

    request.assert_called_once_with(
        "https://example.com/access.log",
        headers={"User-Agent": "nginx-log-processor/1.0"},
        stream=True,
        timeout=DOWNLOAD_TIMEOUT,
    )
    response.raise_for_status.assert_called_once_with()


def test_fetch_log_file_rejects_non_http_url():
    with pytest.raises(ValueError, match="HTTP or HTTPS"):
        fetch_log_file("file:///etc/passwd")


def test_fetch_log_file_closes_response_on_http_error():
    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError("server error")

    with (
        patch("requests.get", return_value=response),
        pytest.raises(requests.HTTPError, match="server error"),
    ):
        fetch_log_file("https://example.com/access.log")

    response.close.assert_called_once_with()
