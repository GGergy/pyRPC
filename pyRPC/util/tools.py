import json
import telebot
import os
from functools import lru_cache


def init():
    if not os.path.isfile('pyrpc.cfg'):
        with open('pyrpc.cfg', mode='w') as wf:
            wf.write('{"lexemas": {}}')
        return {"lexemas": {}}
    with open('pyrpc.cfg') as rf:
        dat = json.load(rf)
        # dat['lexemas'] = {}
        return dat


data = init()
lens = 0


def load_bot():
    if data.get('token', False):
        if not data.get('host', False):
            print('please, start the bot')
        return telebot.TeleBot(data['token'])
    token = input("couldn't find the bot token, create a telegram bot and send the token: ")
    print('done! now, start bot')
    with open('pyrpc.cfg', mode='w') as wf:
        data['token'] = token
        json.dump(data, wf)
    return telebot.TeleBot(token)


def create_host(chat_id):
    if data.get('host', False):
        return
    with open('pyrpc.cfg', mode='w') as wf:
        data['host'] = chat_id
        json.dump(data, wf)
    return True


def reset_token():
    with open('pyrpc.cfg', mode='w') as wf:
        data.pop('token')
        json.dump(data, wf)


def explore(path):
    answer = [f for f in os.scandir(unlex(path))]
    folders, files = [], []
    for item in answer:
        index = lex(item.name)
        if item.is_dir():
            folders.append((index, item.name))
        else:
            files.append((index, item.name))
    return folders, files


@lru_cache
def lex(arg):
    global lens
    if arg not in data['lexemas'].items():
        data['lexemas'][str(lens + 1)] = arg
        lens += 1
        with open('pyrpc.cfg', mode='w') as wf:
            json.dump(data, wf)
        return lens
    for key, item in data['lexemas'].values():
        if item == arg:
            return key


@lru_cache
def unlex(arg):
    return '/'.join([data['lexemas'][item] if item != '.' else item for item in arg.split('/')])
