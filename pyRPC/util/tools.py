import json
import telebot
import os
from functools import lru_cache


data, base = dict(), str()


def init(file):
    global data, base
    base = file[:file.rfind('\\')]
    with open(f'{base}/assets/config.json') as rf:
        data = json.load(rf)


@lru_cache
def create_bot(token):
    try:
        bot = telebot.TeleBot(token)
    except:
        return False
    return bot


def load_bot():
    if data.get('token', False):
        return create_bot(data['token'])
    token = input("couldn't find the bot token, create a telegram bot and send the token: ")
    while not create_bot(token):
        token = input("token doesn't work, send again: ")
    print('done! now, start bot')
    with open(f'{base}/assets/config.json', mode='w') as wf:
        data['token'] = token
        json.dump(data, wf)
    return create_bot(token)


def create_host(chat_id):
    if data.get('host', False):
        return
    with open(f'{base}/assets/config.json', mode='w') as wf:
        data['host'] = chat_id
        json.dump(data, wf)
    return True


def reset_token():
    with open(f'{base}/assets/config.json', mode='w') as wf:
        data.pop('token')
        json.dump(data, wf)


def explore(path):
    answer = [f for f in os.scandir(path)]
    folders, files = [], []
    for item in answer:
        if item.is_dir():
            folders.append(item.name)
        else:
            files.append(item.name)
    return folders, files
