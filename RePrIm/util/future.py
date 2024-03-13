import os
import subprocess
import threading
import time
from unidecode import unidecode

import telebot.apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import TeleBot


mk = InlineKeyboardMarkup()
mk.row(InlineKeyboardButton('❌', callback_data='{"handler": "close"}'))

pid = 0
processes = {}
bot = TeleBot("token")
host = "my_chat_id"


class TGShell:
    def __init__(self, handler: TeleBot):
        env = os.environ.copy()
        self.handler = handler
        self.buff = ""
        self._update = False
        self.terminal = subprocess.Popen('cmd.exe', stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT, shell=True, env=env)
        self.remote_shell_id = self.create_output_message()
        self.writer = threading.Thread(target=self.handle_output)
        self.writer.start()
        self.update_daemon = threading.Thread(target=self.update_shell)
        self.update_daemon.start()

    def handle_output(self):
        while True:
            data = self.terminal.stdout.read(1).decode("cp866")
            if not data:
                break
            self.buff += data
            self._update = True

    def create_output_message(self):
        message = "terminal:\n"

        return self.handler.send_message(text=message, chat_id=host).id

    def update_shell(self):
        while self.terminal.poll() is None:
            if self._update:
                time.sleep(0.2)
                try:
                    self.handler.edit_message_text(message_id=self.remote_shell_id, chat_id=host,
                                                   text="terminal:\n" + self.crop_buff())
                except telebot.apihelper.ApiTelegramException as e:
                    print(e)
                self._update = False
            time.sleep(0.5)

    def crop_buff(self):
        if len(self.buff) > 4000:
            return self.buff[len(self.buff) - 4000:]
        return self.buff

    def write_to_stdin(self, data: str):
        data = unidecode(data) + "\n"
        self.terminal.stdin.write(data.encode("cp866"))
        self.terminal.stdin.flush()


shell = TGShell(bot)


@bot.message_handler(content_types=["text"])
def handle_message(message):
    shell.write_to_stdin(message.text)
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)


bot.infinity_polling()
