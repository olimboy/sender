from django.contrib import admin
from .models import Bot, Sender


admin.site.register([Bot, Sender])
