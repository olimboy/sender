from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from app.models import Bot, Sender, FORWARD
from app.forms import Forward
from app import worker, utils


@login_required(login_url='/admin')
def index(request):
    bots = Bot.objects.all()
    return render(request, 'index.html', {'bots': bots})


@login_required(login_url='/admin')
def bot_view(request, pk):
    bot = get_object_or_404(Bot, pk=pk)
    senders = bot.sender_set.all()
    return render(request, 'view.html', {'bot': bot, 'senders': senders})


@login_required(login_url='/admin')
def forward(request):
    if request.method == 'POST':
        obj = Forward(request.POST)
        if not obj.errors:
            bot_id = obj.cleaned_data['bot']
            bot = Bot.objects.filter(pk=bot_id).first()
            parts = utils.parts(bot, obj.cleaned_data['instance_count'])
            print(parts)
            for part in parts:
                sender = Sender()
                sender.bot_id = bot_id
                sender.function = FORWARD
                sender.value = obj.cleaned_data
                sender.current_id = part[0]
                sender.end_id = part[1]
                sender.total = part[2]
                sender.save()
            # return redirect(request.headers.get('Referer'))
            # pass
            # sender = Sender()
            # sender.bot_id = bot_id
            # sender.function = FORWARD
            # sender.value = obj.cleaned_data
            # sender.save()
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
    return redirect(request.headers.get('Referer'))
