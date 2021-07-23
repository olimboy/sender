from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from app.models import Bot, Sender, FORWARD
from app.forms import Forward
from app import worker


@login_required(login_url='/admin')
def index(request):
    senders = Sender.objects.all()
    return render(request, 'index.html', {'senders': senders})


@login_required(login_url='/admin')
def forward(request):
    if request.method == 'POST':
        obj = Forward(request.POST)
        if not obj.errors:
            sender = Sender()
            sender.bot_id = obj.cleaned_data['bot']
            sender.function = FORWARD
            sender.value = obj.cleaned_data
            sender.save()
    bots = Bot.objects.all()
    return render(request, 'forward.html', {'bots': bots})


@login_required(login_url='/admin')
def set_status(request):
    if request.method == 'POST':
        sender = Sender.objects.filter(pk=request.POST.get('id')).first()
        status = int(request.POST.get('status'))
        if sender and status in (0, 1):
            sender.status = status
            sender.save()
            if sender.status == 1:
                worker.load(sender)
    return redirect('/')
