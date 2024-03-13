import json
import subprocess
import telebot
import os
from functools import lru_cache

try:
    from .hardware_monitor import fetch_stats
    hm_supported = True
except:
    hm_supported = False


def init():
    if not os.path.isfile('reprim.rpc'):
        with open('reprim.rpc', mode='w') as wf:
            wf.write('{"lexemas": {}}')
        return {"lexemas": {}}
    with open('reprim.rpc') as rf:
        dat = json.load(rf)
        return dat


data = init()
lens = len(data['lexemas'].keys())


def load_bot():
    if data.get('token', False):
        if not data.get('host', False):
            print('please, start the bot')
        return telebot.TeleBot(data['token'])
    token = input("couldn't find the bot token, create a telegram bot and send the token: ")
    print('done! now, start bot')
    with open('reprim.rpc', mode='w') as wf:
        data['token'] = token
        data['wait_for_input'] = False
        data['input'] = None
        json.dump(data, wf)
    return telebot.TeleBot(token)


def create_host(chat_id):
    if data.get('host', False):
        return
    with open('reprim.rpc', mode='w') as wf:
        data['host'] = chat_id
        json.dump(data, wf)
    return True


def reset_token():
    with open('reprim.rpc', mode='w') as wf:
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
        with open('reprim.rpc', mode='w') as wf:
            json.dump(data, wf)
        return lens
    for key, item in data['lexemas'].values():
        if item == arg:
            return key


@lru_cache
def unlex(arg):
    return '/'.join([data['lexemas'][item] if item != '.' else item for item in arg.split('/')])


def get_sensors():
    if hm_supported:
        return "\n".join(fetch_stats())
    else:
        return "your pc is not supported hardware monitor"


def execute_command(command, directory):
    process = subprocess.Popen(command.split(), shell=True, stdout=subprocess.PIPE, cwd=directory)
    return process.communicate('', timeout=60)[0][:4096]
