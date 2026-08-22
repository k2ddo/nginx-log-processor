from django.db import models


class LogEntry(models.Model):
    """A normalized entry imported from an Nginx access log."""

    date = models.DateTimeField("Дата", null=True, db_index=True)
    ip_address = models.GenericIPAddressField("IP адрес", null=True, db_index=True)
    user = models.CharField("Имя пользователя", max_length=255, blank=True, default="")
    http_method = models.CharField(
        "HTTP метод", max_length=10, blank=True, default="", db_index=True
    )
    request_uri = models.TextField("URI запроса", blank=True, default="")
    response_code = models.PositiveSmallIntegerField("Код ответа", null=True, db_index=True)
    response_size = models.PositiveBigIntegerField("Размер ответа", null=True)

    class Meta:
        verbose_name = "Лог запись"
        verbose_name_plural = "Лог записи"
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.date} - {self.http_method} {self.request_uri} - {self.response_code}"
