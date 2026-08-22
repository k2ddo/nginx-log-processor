from datetime import datetime
from typing import BinaryIO
from urllib.parse import urlparse

import ijson
import requests
from django.db import transaction

from logs.models import LogEntry

DEFAULT_BATCH_SIZE = 1_000
DOWNLOAD_TIMEOUT = (5, 60)


def fetch_log_file(link: str) -> requests.Response:
    """Open an HTTP stream for a remote log file."""
    if urlparse(link).scheme not in {"http", "https"}:
        raise ValueError("the log URL must use HTTP or HTTPS")

    response = requests.get(
        link,
        headers={"User-Agent": "nginx-log-processor/1.0"},
        stream=True,
        timeout=DOWNLOAD_TIMEOUT,
    )
    try:
        response.raise_for_status()
    except requests.RequestException:
        response.close()
        raise
    return response


def parse_and_store_logs(
    log_stream: BinaryIO,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> int:
    """Stream log records into the database and return the imported count."""
    if batch_size < 1:
        raise ValueError("batch_size must be greater than zero")

    entries: list[LogEntry] = []
    imported_count = 0

    try:
        for data in ijson.items(log_stream, "", multiple_values=True):
            if not isinstance(data, dict):
                raise ValueError("each log record must be a JSON object")
            entries.append(process_log(data))
            if len(entries) >= batch_size:
                imported_count += _store_batch(entries)
    except ijson.IncompleteJSONError:
        if entries or imported_count:
            raise

    if entries:
        imported_count += _store_batch(entries)

    return imported_count


def _store_batch(entries: list[LogEntry]) -> int:
    batch_length = len(entries)
    with transaction.atomic():
        LogEntry.objects.bulk_create(entries)
    entries.clear()
    return batch_length


def process_log(data: dict) -> LogEntry:
    """Convert a structured Nginx record into an unsaved model instance."""
    http_method, request_uri = parse_request(data.get("request"))
    return LogEntry(
        date=parse_date(data.get("time")),
        ip_address=data.get("remote_ip"),
        user=_optional_text(data.get("remote_user")),
        http_method=http_method or "",
        request_uri=request_uri or "",
        response_code=data.get("response"),
        response_size=data.get("bytes"),
    )


def _optional_text(value: object) -> str:
    return "" if value is None or value == "-" else str(value)


def parse_date(date_string: str | None) -> datetime | None:
    """Parse an Nginx timestamp."""
    if not date_string:
        return None
    return datetime.strptime(date_string, "%d/%b/%Y:%H:%M:%S %z")


def parse_request(request_string: str | None) -> tuple[str | None, str | None]:
    """Extract the HTTP method and URI from an Nginx request field."""
    if request_string:
        parts = request_string.split()
        if len(parts) >= 2:
            return parts[0], parts[1]
    return None, None
