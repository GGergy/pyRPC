import json
import telebot
import os


def init():
    if not os.path.isfile('pyrpc.cfg'):
        with open('pyrpc.cfg', mode='w') as wf:
            wf.write('{}')
        return {}
    with open('pyrpc.cfg') as rf:
        return json.load(rf)


data = init()


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


def reset_token():
    with open('pyrpc.cfg', mode='w') as wf:
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
