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
                self.handler.send_message(chat_id=data['host'], text=f"Console output:\n{self.update}"[:4096],
                                          reply_markup=mk)
                self.update = ""
            if self._closed:
                return

    def close(self):
        self._closed = True


class RePrImInput:
    def __init__(self, handler):
        self.handler = handler

    def readline(self):
        self.handler.send_message(chat_id=data['host'], text=f"Programm ask to input", reply_markup=mk)
        update = False
        while not update:
            with open('.rtmp') as f:
                update = f.read().strip()
        with open('.rtmp', 'w') as f:
            f.write('')
        return update

    def close(self):
        pass
