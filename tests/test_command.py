from io import BytesIO, StringIO
from unittest.mock import MagicMock, patch

import pytest
import requests
from django.core.management import call_command
from django.core.management.base import CommandError

from logs.models import LogEntry

LOG_DATA = b'{"request":"GET /health HTTP/1.1","response":200,"bytes":2}'


@pytest.mark.django_db
def test_processlog_command_imports_remote_file():
    response = MagicMock()
    response.raw = BytesIO(LOG_DATA)
    response.__enter__.return_value = response
    output = StringIO()

    with patch(
        "logs.management.commands.processlog.fetch_log_file", return_value=response
    ) as fetch:
        call_command("processlog", "https://example.com/access.log", stdout=output)

    fetch.assert_called_once_with("https://example.com/access.log")
    response.__exit__.assert_called_once()
    assert LogEntry.objects.count() == 1
    assert "Imported 1 log entries" in output.getvalue()


def test_processlog_command_exits_with_error_on_download_failure():
    with (
        patch(
            "logs.management.commands.processlog.fetch_log_file",
            side_effect=requests.Timeout("timed out"),
        ),
        pytest.raises(CommandError, match="Could not import log file: timed out"),
    ):
        call_command("processlog", "https://example.com/access.log")
