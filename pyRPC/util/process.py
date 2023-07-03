import json
import os
import sys
import subprocess
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from .tools import data


processes = []


class Process:
    def __init__(self, file, absfile, default_dir, handler):
        self.file = file
        self.absfile = absfile
        os.chdir(os.path.dirname(absfile))
        args = [sys.executable, absfile] if absfile.endswith('.py') else [absfile]
        self.process = subprocess.Popen(args=args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE)
        os.chdir(default_dir)
        self.handler = handler
        self.name = os.path.split(absfile)[1]
        processes.append(self)
        self.thread = Thread(target=self.daemon)
        self.thread.start()

    def daemon(self):
        mk = InlineKeyboardMarkup()
        mk.row(InlineKeyboardButton('communicate',
                                    callback_data=json.dumps({"handler": "communicate", "data": self.file})))
        mk.row(InlineKeyboardButton('❌', callback_data='{"handler": "close"}'))
        while self.process.poll() is None:
            out = self.process.stdout.readline().decode(encoding='utf-8')
            if out:
                self.handler.send_message(chat_id=data['host'], text=f"out from {self.name}:\n{out}", reply_markup=mk)
        mk = InlineKeyboardMarkup()
        mk.row(InlineKeyboardButton('❌', callback_data='{"handler": "close"}'))
        self.handler.send_message(chat_id=data['host'], text=f"process {self.name} was completed", reply_markup=mk)

    def communicate(self, info):
        self.process.stdin.write(str(info).encode())
        self.process.stdin.close()

    def kill(self):
        self.process.kill()
