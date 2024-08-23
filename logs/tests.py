from io import StringIO
from datetime import datetime, timezone, timedelta
from django.test import TestCase
from .models import LogEntry
from .management.commands._processlog_services import (
    parse_and_store_logs,
    process_log,
    parse_date,
    parse_request,
)

class ProcessLogCase(TestCase):

    def setUp(self):
        self.log_data = '''
        {"time": "17/May/2015:08:05:32 +0000", "remote_ip": "192.168.1.1", "remote_user": "test_user", "request": "GET /downloads/product_1 HTTP/1.1", "response": 200, "bytes": 1024}
        {"time": "17/May/2015:08:05:33 +0000", "remote_ip": "192.168.1.2", "remote_user": "test_user2", "request": "POST /downloads/product_2 HTTP/1.1", "response": 404, "bytes": 2048}
        '''
        self.log_object = {
            'time': '17/May/2015:08:05:32 +0000',
            'remote_ip': '192.168.1.1',
            'remote_user': 'test_user',
            'request': 'GET /downloads/product_1 HTTP/1.1',
            'response': 200,
            'bytes': 1024
        }

    def test_parse_and_store_logs(self):
        log_stream = StringIO(self.log_data)  # Создание потока
        parse_and_store_logs(log_stream, batch_size=1)

        self.assertEqual(LogEntry.objects.count(), 2)

        log_entries = LogEntry.objects.all().order_by('ip_address')
        first_log_entry = log_entries[0]
        second_log_entry = log_entries[1]

        self.assert_log_entry(first_log_entry, '192.168.1.1', 'test_user', 'GET', '/downloads/product_1', 200, 1024)
        self.assert_log_entry(second_log_entry, '192.168.1.2', 'test_user2', 'POST', '/downloads/product_2', 404, 2048)

    def test_process_log(self):
        log_entry = process_log(self.log_object)
        expected_date = datetime(2015, 5, 17, 8, 5, 32, tzinfo=timezone(timedelta(hours=0)))
        
        self.assertEqual(log_entry.date, expected_date)
        self.assert_log_entry(log_entry, '192.168.1.1', 'test_user', 'GET', '/downloads/product_1', 200, 1024)

    def test_parse_date(self):
        date_str = '17/May/2015:08:05:32 +0000'
        expected_date = datetime(2015, 5, 17, 8, 5, 32, tzinfo=timezone(timedelta(hours=0)))
        self.assertEqual(parse_date(date_str), expected_date)
        self.assertIsNone(parse_date(None))

    def test_parse_request(self):
        request_str = 'GET /downloads/product_1 HTTP/1.1'
        http_method, request_uri = parse_request(request_str)
        self.assertEqual(http_method, 'GET')
        self.assertEqual(request_uri, '/downloads/product_1')

        http_method, request_uri = parse_request(None)
        self.assertIsNone(http_method)
        self.assertIsNone(request_uri)

    def assert_log_entry(self, log_entry, ip_address, user, http_method, request_uri, response_code, response_size):
        self.assertEqual(log_entry.ip_address, ip_address)
        self.assertEqual(log_entry.user, user)
        self.assertEqual(log_entry.http_method, http_method)
        self.assertEqual(log_entry.request_uri, request_uri)
        self.assertEqual(log_entry.response_code, response_code)
        self.assertEqual(log_entry.response_size, response_size)

