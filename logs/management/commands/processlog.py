import requests
from django.core.management.base import BaseCommand, CommandError

from ._processlog_services import fetch_log_file, parse_and_store_logs


class Command(BaseCommand):
    help = "Download a structured Nginx log and import it into the database"

    def add_arguments(self, parser) -> None:
        parser.add_argument("url", help="HTTP(S) URL of the log file")
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1_000,
            help="Number of entries inserted per database query (default: 1000)",
        )

    def handle(self, *args, **options) -> None:
        url = options["url"]
        self.stdout.write(f"Downloading log file: {url}")

        try:
            with fetch_log_file(url) as response:
                imported_count = parse_and_store_logs(response.raw, options["batch_size"])
        except (requests.RequestException, ValueError) as exc:
            raise CommandError(f"Could not import log file: {exc}") from exc

        self.stdout.write(self.style.SUCCESS(f"Imported {imported_count} log entries"))
