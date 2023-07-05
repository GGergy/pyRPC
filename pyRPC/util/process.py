import json
import os
import sys
import subprocess
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from .tools import data


pid = 0
processes = {}


class Process:
    def __init__(self, absfile, default_dir, handler):
        global pid
        self.absfile = absfile
        self.id = pid + 1
        pid += 1
        os.chdir(os.path.dirname(absfile))
        args = [sys.executable, absfile] if absfile.endswith('.py') else [absfile]
        self.process = subprocess.Popen(args=args, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE)
        os.chdir(default_dir)
        self.handler = handler
        self.name = os.path.split(absfile)[1]
        processes[self.id] = self
        self.thread = Thread(target=self.daemon)
        self.thread.start()

    def daemon(self):
        mk = InlineKeyboardMarkup()
        mk.row(InlineKeyboardButton('communicate',
                                    callback_data=json.dumps({"handler": "communicate", "data": self.id})))
        mk.row(InlineKeyboardButton('❌', callback_data='{"handler": "close"}'))
        while self.alive():
            out = self.process.stdout.readline().decode(encoding='utf-8')
            if out:
                self.handler.send_message(chat_id=data['host'], text=f"out from {self.name}:\n{out}", reply_markup=mk)
        mk = InlineKeyboardMarkup()
        mk.row(InlineKeyboardButton('❌', callback_data='{"handler": "close"}'))
        err = self.process.stderr.read().decode(encoding='utf-8')
        self.handler.send_message(chat_id=data['host'],
                                  text=f"process {self.name} was completed{' with error ' + err if err else ''}",
                                  reply_markup=mk)
        processes.pop(self.id)

    def communicate(self, info):
        self.process.stdin.write(str(info).encode())
        self.process.stdin.close()

    def kill(self):
        if self.name.endswith('.py'):
            self.process.kill()
        else:
            subprocess.Popen(f'taskkill /im {self.name} /f')

    def alive(self):
        return self.process.poll() is None
