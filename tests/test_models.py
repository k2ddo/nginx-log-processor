from logs.models import LogEntry


def test_log_entry_string_representation():
    entry = LogEntry(http_method="GET", request_uri="/", response_code=200)

    assert str(entry) == "None - GET / - 200"
