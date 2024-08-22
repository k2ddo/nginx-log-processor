from django.db import models


class LogEntry(models.Model):
    """Модель для хранения записей из лога"""
    date = models.DateTimeField('Дата')
    ip_address = models.GenericIPAddressField('IP адрес')
    user = models.CharField('Имя пользователя', max_length=255)
    http_method = models.CharField('HTTP метод', max_length=10)
    request_uri = models.TextField('URI запроса')
    response_code = models.PositiveSmallIntegerField('Код ответа')
    response_size = models.IntegerField('Размер ответа')

    def __str__(self):
        return f"{self.date} - {self.http_method} {self.request_uri} - {self.response_code}"
