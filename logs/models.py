from django.db import models


class LogEntry(models.Model):
    """Модель для хранения записей из лога"""
    date = models.DateTimeField('Дата', null=True)
    ip_address = models.GenericIPAddressField('IP адрес', null=True)
    user = models.CharField('Имя пользователя', max_length=255, blank=True, default='')
    http_method = models.CharField('HTTP метод', max_length=10, blank=True, default='')
    request_uri = models.TextField('URI запроса', blank=True, default='')
    response_code = models.PositiveSmallIntegerField('Код ответа', null=True)
    response_size = models.IntegerField('Размер ответа', null=True)

    def __str__(self):
        return f"{self.date} - {self.http_method} {self.request_uri} - {self.response_code}"

    class Meta:
        verbose_name = 'Лог запись'
        verbose_name_plural = 'Лог записи'

        ordering = ['-date']
