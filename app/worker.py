import glob
import os
import sqlite3
import threading
import time

from pyrogram import Client
from pyrogram.errors.exceptions.bad_request_400 import InputUserDeactivated, UserIsBlocked
from pyrogram.client.types import InlineKeyboardMarkup, InlineKeyboardButton
from .models import Sender, FORWARD, SEND_MESSAGE
from time import sleep
from threading import Thread
from dotenv import load_dotenv
from requests import post

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

    def admin_id(self):
        return 268223984

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
        text = """Ikkinchi jaxon urushi nechanchi yilda tugagan? Bu savolga 95% inson xato javob bermoqda. Siz bilasizmi? Bilimingizni sinab ko'ring."""
        keyboard = [[
            InlineKeyboardButton('1945-yil 17-may', url='https://t.me/PhotoTarix/219'),
            InlineKeyboardButton('1945-yil 9-may', url='https://t.me/PhotoTarix/219'),
        ], [
            InlineKeyboardButton('1945-yil 3-avgust', url='https://t.me/PhotoTarix/219'),
            InlineKeyboardButton('1945-yil 2-sentabr', url='https://t.me/PhotoTarix/219'),
        ]]
        markup = InlineKeyboardMarkup(keyboard)
        conn = sqlite3.connect(self.sender.bot.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f'SELECT id FROM bot_user WHERE id >= {self.sender.current_id} AND id <= {self.sender.end_id} AND active ORDER BY id LIMIT 10')
        res = cursor.fetchall()
        for cur in res:
            chat_id = cur[0]
            self.sender.current_id = chat_id + 1
            try:
                # self.client.forward_messages(chat_id, self.sender.value['from_chat_id'],
                #                              message_ids=self.sender.value['message_id'])
                # self.client.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')
                self.client.send_photo(chat_id, 'https://t.me/PhotoTarix/219', caption=text, reply_markup=markup,
                                       parse_mode='Markdown')

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
        conn.close()

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
