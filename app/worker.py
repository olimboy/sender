import glob
import os
import sqlite3

from pyrogram import Client
from pyrogram.errors.exceptions.bad_request_400 import InputUserDeactivated, UserIsBlocked
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
    if sender.pk in clients:
        return clients[sender.pk]
    client = Client(f'sessions/sender_{sender.pk}', os.getenv('API_ID'), os.getenv('API_HASH'),
                    bot_token=sender.bot.token)
    print('Client Starting')
    client.start()
    clients[sender.pk] = client
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
        text = """Va nihoyat, [gazuz_bot](http://t.me/gazuz_bot) 🔥 Gaz balansini tekshirish botimiz ham ishga tushdi 😊.
**Do'stlaringizga ulashishni unutmang!** 🗣"""
        conn = sqlite3.connect(self.sender.bot.db_path)
        cursor = conn.cursor()
        cursor.execute(f'SELECT id FROM bot_user WHERE id > {self.sender.current_id} AND active ORDER BY id LIMIT 10')
        res = cursor.fetchall()
        for cur in res:
            # sleep(1)
            chat_id = cur[0]
            self.sender.current_id = chat_id
            try:
                # self.client.forward_messages(chat_id, self.sender.value['from_chat_id'],
                #                              message_ids=self.sender.value['message_id'])
                self.client.send_message(chat_id, text, parse_mode='Markdown')
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
        print('Starting Thread')
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
