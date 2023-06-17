import os.path
from io import BytesIO
from .util import tools
from telebot import types


tools.init(__file__)
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
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton('/explorer'), types.KeyboardButton('/processes'), row_width=2)
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
        print(path)
        btns.append(types.InlineKeyboardButton(text='🔙', callback_data=f"explore::{os.path.dirname(path)}"))
        if len(path.split('\\')) > 2:
            btns.append(types.InlineKeyboardButton(text='🏠', callback_data=f"explore::."))
    btns.append(types.InlineKeyboardButton(text='❌', callback_data='close'))
    markup.row(*btns)
    markup.row(types.InlineKeyboardButton(text='🔄', callback_data=f"explore::{path}"),
               types.InlineKeyboardButton(text='📤upload', callback_data=f"upload::{path}"))
    return markup


@bot.callback_query_handler(func=lambda call: call.data.startswith('explore'))
def handle_explorer(call):
    if not access(call.message):
        return
    path = call.data.split("::")[1]
    msg = explorer_func(path)
    if not msg:
        bot.answer_callback_query(callback_query_id=call.id, text='its empty folder')
        return
    try:
        bot.edit_message_text(text='your files', reply_markup=msg, chat_id=call.message.chat.id,
                              message_id=call.message.id)
    except:
        bot.answer_callback_query(callback_query_id=call.id, text='there are no updates')


@bot.callback_query_handler(func=lambda call: call.data.startswith('selectfile'))
def file_view(call):
    filename = call.data.split("::")[1]
    notpath = filename[filename.rfind('\\') + 1:]
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text='⬇️download', callback_data=f"download::{filename}"))
    markup.row(types.InlineKeyboardButton(text='🗑️delete', callback_data=f"delete::{filename}"))
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


@bot.callback_query_handler(func=lambda call: call.data == 'close')
def close(call):
    bot.delete_message(message_id=call.message.id, chat_id=call.message.chat.id)


@bot.message_handler(content_types=['text', 'audio', 'photo', 'video', 'media', 'file', 'voice', 'video_note'])
def deleter(message):
    bot.delete_message(message.chat.id, message.id)


try:
    print('host created, dont shutdown your PC')
    bot.infinity_polling()
except:
    tools.reset_token()
