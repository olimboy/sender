# Generated by Django 3.2.4 on 2021-08-16 02:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_sender_end_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='sender',
            name='total',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sender',
            name='current_id',
            field=models.BigIntegerField(),
        ),
    ]