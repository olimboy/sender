from django.db import models

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


class Sender(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    function = models.IntegerField(choices=sender_functions)
    value = models.JSONField()
    current_id = models.BigIntegerField(default=0)
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


class Forward:
    bot = 0
    from_chat_id = 0
    message_id = 0
