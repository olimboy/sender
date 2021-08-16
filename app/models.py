from django.db import models
from django.db.models import Sum

FORWARD = 0
SEND_MESSAGE = 1

sender_functions = (
    (FORWARD, 'Forward'),
    (SEND_MESSAGE, 'SendMessage')
)


class Bot(models.Model):
    name = models.CharField(max_length=255)
    token = models.CharField(max_length=1024)
    db_path = models.CharField(max_length=1024)
    http_url = models.CharField(max_length=1024)

    def __str__(self):
        return self.name

    @property
    def success(self):
        return Sender.objects.filter(bot=self).aggregate(success=Sum('success'))['success'] or 0

    @property
    def error(self):
        return Sender.objects.filter(bot=self).aggregate(error=Sum('error'))['error'] or 0

    @property
    def total(self):
        return Sender.objects.filter(bot=self).aggregate(total=Sum('total'))['total'] or 0

    @property
    def current(self):
        total = self.total
        if total == 0:
            total = 1
        return '{:.1f}'.format((self.success + self.error) / total * 100)


class Sender(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    function = models.IntegerField(choices=sender_functions)
    value = models.JSONField()
    current_id = models.BigIntegerField()
    end_id = models.BigIntegerField()
    total = models.IntegerField()
    success = models.IntegerField(default=0)
    error = models.IntegerField(default=0)
    status = models.IntegerField(choices=(
        (0, 'Stopped'),
        (1, 'Running'),
    ), default=0)

    def __str__(self):
        return f'{self.bot.name} - {self.get_function_display()}'

    @property
    def status_not(self):
        return self.status ^ 1

    @property
    def current(self):
        return '{:.1f}'.format((self.success + self.error) / self.total * 100)


class Forward:
    bot = 0
    from_chat_id = 0
    message_id = 0
