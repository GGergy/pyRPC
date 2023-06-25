import os

import telebot.apihelper

if __name__ == "__main__":
    os.chdir(os.path.split(os.getcwd())[0])
    os.system("python test.py")
    quit()
from io import BytesIO
from .util import tools
from telebot import types

tools.init()
bot = tools.load_bot()


def access(message):
    if message.chat.id != tools.data['host']:
        bot.send_message(chat_id=message.chat.id, text='you have no access to this RPC')
    else:
        return True


@bot.message_handler(commands=['start'])
def start(message):
    bot.delete_message(message_id=message.id, chat_id=message.chat.id)
    tools.create_host(message.chat.id)
    if not access(message):
        return
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton('explorer', callback_data="explore::.::1"))
    markup.row(types.InlineKeyboardButton('process manager', callback_data='process'))
    bot.send_message(chat_id=message.chat.id, text='host connected successfully', reply_markup=markup)


@bot.message_handler(commands=['explorer'])
def explorer(message):
    bot.delete_message(message_id=message.id, chat_id=message.chat.id)
    if not access(message):
        return
    msg = explorer_func('.')
    bot.send_message(text='your files', reply_markup=msg if msg else None, chat_id=message.chat.id)


def explorer_func(path):
    folders, files = tools.explore(path)
    if not folders and not files:
        return
    markup = types.InlineKeyboardMarkup()
    buttons = 0
    for folder in folders:
        if buttons >= 45:
            break
        markup.row(types.InlineKeyboardButton(text=f'📁{folder}',
                                              callback_data=f"explore::{os.path.join(path, folder)}"))
        buttons += 1
    for file in files:
        if buttons >= 45:
            break
        markup.row(types.InlineKeyboardButton(text=f'📄{file}',
                                              callback_data=f"selectfile::{os.path.join(path, file)}"))
        buttons += 1
    btns = []
    if path != '.':
        btns.append(types.InlineKeyboardButton(text='🔙', callback_data=f"explore::{os.path.dirname(path)}"))
        if len(path.split('\\')) > 2:
            btns.append(types.InlineKeyboardButton(text='🏠', callback_data=f"explore::."))
    markup.row(*btns)
    markup.row(types.InlineKeyboardButton(text='🔄', callback_data=f"explore::{path}"),
               types.InlineKeyboardButton(text='📤upload', callback_data=f"upload::{path}"))
    markup.row(types.InlineKeyboardButton(text='❌', callback_data='close'))
    return markup


@bot.callback_query_handler(func=lambda call: call.data.startswith('explore'))
def handle_explorer(call):
    if not access(call.message):
        return
    path = call.data.split("::")[1]
    new = len(call.data.split("::")) == 3
    msg = explorer_func(path)
    if not msg:
        bot.answer_callback_query(callback_query_id=call.id, text='its empty folder')
        return
    try:
        if new:
            bot.send_message(text='your files', reply_markup=msg, chat_id=call.message.chat.id)
            bot.answer_callback_query(callback_query_id=call.id)
        else:
            bot.edit_message_text(text='your files', reply_markup=msg, chat_id=call.message.chat.id,
                                  message_id=call.message.id)
    except telebot.apihelper.ApiTelegramException:
        bot.answer_callback_query(callback_query_id=call.id, text='there are not updates')


@bot.callback_query_handler(func=lambda call: call.data.startswith('selectfile'))
def file_view(call):
    filename = call.data.split("::")[1]
    notpath = filename[filename.rfind('\\') + 1:]
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text='⬇️download', callback_data=f"download::{filename}"))
    markup.row(types.InlineKeyboardButton(text='🗑️delete', callback_data=f"&delete::{filename}"))
    markup.row(types.InlineKeyboardButton(text='🔄replace', callback_data=f"replace::{filename}"))
    if notpath.endswith('.exe') or notpath.endswith('.py'):
        markup.row(types.InlineKeyboardButton(text='▶️run', callback_data=f"run::{filename}"))
    markup.row(types.InlineKeyboardButton(text='🔙', callback_data=f"explore::{os.path.dirname(filename)}"),
               types.InlineKeyboardButton(text='❌', callback_data='close'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f'selected file - {notpath}',
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('download'))
def download(call):
    filename = call.data.split('::')[1]
    with open(filename, mode='rb') as rf:
        data = BytesIO(rf.read())
        data.name = filename[filename.rfind('\\') + 1:]
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text='❌', callback_data='close'))
    bot.send_document(chat_id=call.message.chat.id, reply_markup=markup, document=data)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete'))
def delete(call):
    bot.answer_callback_query(call.id)
    filename, action = call.data.split('::')[1:]
    if action:
        os.remove(filename)
    msg = explorer_func(os.path.split(filename)[0])
    if not msg:
        msg = explorer_func('.')
    bot.edit_message_text(text='your files', reply_markup=msg, chat_id=call.message.chat.id,
                          message_id=call.message.id)


@bot.callback_query_handler(func=lambda call: call.data == 'close')
def close(call):
    bot.delete_message(message_id=call.message.id, chat_id=call.message.chat.id)


@bot.message_handler(content_types=['text', 'audio', 'photo', 'video', 'media', 'file', 'voice', 'video_note'])
def deleter(message):
    bot.delete_message(message.chat.id, message.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('&'))
def conf_action(call):
    callback = call.data[1:]
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton('confirm✅', callback_data=f"{callback}::1"))
    markup.row(types.InlineKeyboardButton("cancel❌", callback_data=f"{callback}::"))
    bot.edit_message_text(message_id=call.message.id, chat_id=call.message.chat.id, text="confirm action:",
                          reply_markup=markup)


try:
    print('host created, dont shutdown your PC')
    bot.infinity_polling()
except:
    tools.reset_token()
