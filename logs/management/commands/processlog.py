import requests
from django.core.management.base import BaseCommand

from ._processlog_services import fetch_log_file, parse_and_store_logs


class Command(BaseCommand):
    help = 'Парсит лог файл и записывает в базу данных'

    def add_arguments(self, parser):
        parser.add_argument('link', type=str, help='Ссылка на лог файл')

    def handle(self, *args, **options):
        link = options['link']

        self.stdout.write(self.style.NOTICE(f'Начало обработки лог файла по ссылке: {link}'))
        
        try:
            log_stream = fetch_log_file(link)
            parse_and_store_logs(log_stream)
            self.stdout.write(self.style.SUCCESS('Лог файл успешно обработан'))
        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f'Ошибка при загрузке файла: {e}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка при обработке файла: {e}'))
