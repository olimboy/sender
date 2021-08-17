import glob
import os
import sqlite3
import threading
import time

from pyrogram import Client
from pyrogram.errors.exceptions.bad_request_400 import InputUserDeactivated, UserIsBlocked
from pyrogram.client.types import InlineKeyboardMarkup, InlineKeyboardButton

from .messages import rec
from .models import Sender, FORWARD, SEND_MESSAGE
from time import sleep
from threading import Thread
from dotenv import load_dotenv
from requests import post

from .utils import get_10_users

load_dotenv()

clients = {}


def remove_session(sender: Sender):
    fileList = glob.glob(f'sessions/sender_{sender.pk}*')
    # Iterate over the list of filepaths & remove each file.
    for filePath in fileList:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)


def get_client(sender: Sender):
    client_id = sender.pk
    if client_id in clients:
        return clients[client_id]
    client = Client(f'sessions/sender_{client_id}', os.getenv('API_ID'), os.getenv('API_HASH'),
                    bot_token=sender.bot.token)
    print(f'[{client_id}] Client Starting')
    client.start()
    clients[client_id] = client
    return client


class Worker:

    def __init__(self, sender: Sender):
        self.sender = sender
        if sender.status == 1:
            self.client = get_client(sender)
        else:
            self.die()

    def is_active(self):
        sender = Sender.objects.filter(pk=self.sender.pk).first()
        if sender and sender.status == 1:
            return True
        return False

    def die(self):
        print('Client Stopping')
        try:
            self.client.stop()
            remove_session(self.sender)
            clients.pop(self.sender.pk)
        except Exception as e:
            print('Die Err:', e)
        print('Client Stopped')

    def deactivate_user(self, pk):
        try:
            post(f'{self.sender.bot.http_url}/{self.sender.bot.token}/{pk}', json={'active': False})
        except Exception as e:
            print(e)

    # Forward 10 message
    def forward(self):
        res = get_10_users(self.sender)
        for cur in res:
            chat_id = cur[0]
            self.sender.current_id = chat_id + 1
            try:
                rec(self.client, chat_id)
                self.sender.success += 1
            except (UserIsBlocked, InputUserDeactivated) as e:
                self.sender.error += 1
                print(e)
                self.deactivate_user(chat_id)
            except Exception as e:
                self.sender.error += 1
                print(e, 'Unknown')
                self.sender.status = 0
                self.sender.save()
                exit(1)
        if len(res) == 0:
            self.sender.status = 0
            self.sender.save()
        else:
            self.sender.save(update_fields=['success', 'error', 'current_id'])

    def start(self):
        print(f'Starting Thread')
        if self.sender == 0:
            return
        while True:
            if not self.is_active():
                self.die()
                del self
                print('Deleted')
                return
            if self.sender.function == FORWARD:
                self.forward()
            print(f'{self.sender} <{self.sender.pk}> running')


def load(sender: Sender):
    Thread(daemon=True, target=Worker(sender).start).start()
