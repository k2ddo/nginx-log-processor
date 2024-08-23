from typing import Optional
from io import BufferedIOBase
from datetime import datetime

import ijson
import requests

from logs.models import LogEntry


def fetch_log_file(link: str) -> BufferedIOBase:
    """Загружает лог файл по ссылке."""
    response = requests.get(link, stream=True)
    response.raise_for_status()  # Проверка статуса ответа
    return response.raw


def parse_and_store_logs(log_stream, batch_size=1000) -> None:
    """Парсит лог-записи и сохраняет их в базу данных."""
    objects = ijson.items(log_stream, '', multiple_values=True)
    log_entries = []

    for object in objects:
        log_entry = process_log(object)
        log_entries.append(log_entry)

        # Оптимизация массового добавления
        if len(log_entries) >= batch_size:
            LogEntry.objects.bulk_create(log_entries)
            log_entries.clear()

    # Добавление оставшихся log_entries
    if log_entries:
        LogEntry.objects.bulk_create(log_entries)


def process_log(object: dict) -> LogEntry:
    """Обрабатывает лог-запись и возвращает объект LogEntry."""
    date = parse_date(object.get('time'))
    http_method, request_uri = parse_request(object.get('request'))

    return LogEntry(
        date=date,
        ip_address=object.get('remote_ip'),
        user=object.get('remote_user'),
        http_method=http_method,
        request_uri=request_uri,
        response_code=object.get('response'),
        response_size=object.get('bytes')
    )


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Парсит дату из строки в формат datetime."""
    if date_str:
        date_format = "%d/%b/%Y:%H:%M:%S %z"
        return datetime.strptime(date_str, date_format)
    return None


def parse_request(request_str: Optional[str]) -> tuple:
    """Достаёт HTTP метод и URI из строки запроса."""
    if request_str:
        parts = request_str.split()
        if len(parts) >= 2:
            return parts[0], parts[1]
    return None, None

