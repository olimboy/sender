import os

from django.test import TestCase

# Create your tests here.
import asyncio
from threading import Thread
from time import sleep
from dotenv import load_dotenv
from pyrogram import Client

import asyncio
import time

load_dotenv()

workers = []


def f1():
    client = Client('sender', os.getenv('API_ID'), os.getenv('API_HASH'), bot_token='')
    print('Starting')
    client.start()
    print('Started')
    client.send_message(268223984, 'salom')
    client.send_message(268223984, 'salom')
    client.send_message(268223984, 'salom')
    client.stop()

def f2():
    client = Client('sender2', os.getenv('API_ID'), os.getenv('API_HASH'), bot_token='')
    print('Starting')
    client.start()
    print('Started')
    client.send_message(268223984, 'salom')
    client.send_message(268223984, 'salom')
    client.send_message(268223984, 'salom')
    client.stop()


# f1()
# f2()
# exit()
t1 = Thread(target=f1)
t1.start()
t2 = Thread(target=f2).start()