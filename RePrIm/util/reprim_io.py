import json
import threading
import time
from .tools import data
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


mk = InlineKeyboardMarkup()
mk.row(InlineKeyboardButton('❌', callback_data='{"handler": "close"}'))


class RePrImOutput:
    def __init__(self, handler, update_per=2):
        self.update = ""
        self.console = ""
        self.handler = handler
        self.update_per = update_per
        self.handle_thread = threading.Thread(target=self.handle)
        self.handle_thread.start()
        self._closed = False

    def write(self, string):
        self.update += string
        self.console += string

    def flush(self):
        pass

    def handle(self):
        while True:
            time.sleep(self.update_per)
            if self.update:
                self.handler.send_message(chat_id=data['host'], text=f"Console output:\n{self.update}", reply_markup=mk)
                self.update = ""
            if self._closed:
                return

    def close(self):
        self._closed = True


"""
class RePrImInput:
    def __init__(self, handler):
        self.handler = handler

    def readline(self):
        self.handler.send_message(chat_id=data['host'], text=f"Programm ask to input", reply_markup=mk)
        with open('reprim.rpc', encoding='utf-8') as f:
            filedata = json.loads(f.read().strip())
            filedata['wait_for_input'] = True
        with open('reprim.rpc', 'w') as f:
            json.dump(filedata, f)
        update = False
        while not update:
            with open('reprim.rpc') as f:
                print(f.read())
                filedata = json.loads(f.read().strip())
                update = filedata.get('input', None)
        with open('reprim.rpc', 'w') as f:
            filedata['wait_for_input'] = False
            filedata['input'] = None
            json.dump(filedata, f)
        return update

    def close(self):
        pass
"""