from django.forms import Form, IntegerField


class Forward(Form):
    bot = IntegerField()
    from_chat_id = IntegerField()
    message_id = IntegerField()
    instance_count = IntegerField()
