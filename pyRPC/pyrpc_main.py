import json
import os
import telebot.apihelper

if __name__ == "__main__":
    os.chdir(os.path.split(os.getcwd())[0])
    os.system("python test.py")
    quit()
from io import BytesIO
from .util import tools, process
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
    markup.row(types.InlineKeyboardButton('explorer',
                                          callback_data='{"handler": "explore", "data": ".", "new": true}'))
    markup.row(types.InlineKeyboardButton('process manager', callback_data='process'))
    markup.row(types.InlineKeyboardButton("computer info", callback_data='{"handler": "hardware_monitor"}'))
    bot.send_message(chat_id=message.chat.id, text='host connected successfully', reply_markup=markup)


def explorer_func(path):
    folders, files = tools.explore(path)
    if not folders and not files:
        return
    markup = types.InlineKeyboardMarkup()
    buttons = 0
    for folder in folders:
        if buttons >= 45:
            break
        markup.row(types.InlineKeyboardButton(text=f'📁{folder[1]}',
                                              callback_data=json.dumps({"handler": "explore",
                                                                        "data": f"{path}/{folder[0]}"})))
        buttons += 1
    for file in files:
        if buttons >= 45:
            break
        markup.row(types.InlineKeyboardButton(text=f'📄{file[1]}',
                                              callback_data=json.dumps({'handler': "selectfile",
                                                                        "data": f"{path}/{file[0]}"})))
        buttons += 1
    markup.row(types.InlineKeyboardButton(text='🔄', callback_data=json.dumps({"handler": "explore", "data": path})),
               types.InlineKeyboardButton(text='📤upload',
                                          callback_data=json.dumps({"handler": "upload", "data": path})))
    btns = []
    if path != '.':
        btns.append(types.InlineKeyboardButton(text='🔙', callback_data=json.dumps({"handler": "explore",
                                                                                   "data": os.path.split(path)[0]})))
        if len(path.split('/')) > 2:
            btns.append(types.InlineKeyboardButton(text='🏠',  callback_data='{"handler": "explore", "data": "."}'))
    btns.append(types.InlineKeyboardButton(text='❌', callback_data='{"handler": "close"}'))
    markup.row(*btns)
    return markup


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'explore')
def handle_explorer(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    if not access(call.message):
        return
    js = json.loads(call.data)
    msg = explorer_func(js['data'])
    if not msg:
        bot.answer_callback_query(callback_query_id=call.id, text='its empty folder')
        return
    try:
        if js.get('new', False):
            bot.send_message(text='your files', reply_markup=msg, chat_id=call.message.chat.id)
            bot.answer_callback_query(callback_query_id=call.id)
        else:
            bot.edit_message_text(text='your files', reply_markup=msg, chat_id=call.message.chat.id,
                                  message_id=call.message.id)
    except telebot.apihelper.ApiTelegramException:
        bot.answer_callback_query(callback_query_id=call.id, text='there are not updates')


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'selectfile')
def file_view(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    filename = json.loads(call.data)['data']
    file_view_func(filename, call.message.id, call.message.chat.id)


def file_view_func(filename, message_id, chat_id):
    only_name = os.path.split(tools.unlex(filename))[1]
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text='⬇️download',
                                          callback_data=json.dumps({"handler": "download", 'data': filename})))
    markup.row(types.InlineKeyboardButton(text='🗑️delete',
                                          callback_data=json.dumps({"handler": "?delete", "data": filename})))
    markup.row(types.InlineKeyboardButton(text='🔄replace',
                                          callback_data=json.dumps({"handler": "replace", "data": filename})))
    if only_name.endswith('.exe') or only_name.endswith('.py'):
        markup.row(types.InlineKeyboardButton(text='▶️run',
                                              callback_data=json.dumps({"handler": "run", "data": filename})))
    markup.row(types.InlineKeyboardButton(text='🔙', callback_data=json.dumps({"handler": "explore",
                                                                              "data": os.path.dirname(filename)})),
               types.InlineKeyboardButton(text='❌', callback_data='{"handler": "close"}'))
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'selected file - {only_name}',
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'download')
def download(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    filename = tools.unlex(json.loads(call.data)['data'])
    with open(filename, mode='rb') as rf:
        data = BytesIO(rf.read())
        data.name = os.path.split(filename)[1]
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text='❌', callback_data='{"handler": "close"}'))
    try:
        bot.send_document(chat_id=call.message.chat.id, reply_markup=markup, document=data)
        bot.answer_callback_query(callback_query_id=call.id)
    except:
        bot.answer_callback_query(callback_query_id=call.id, text='file is empty')


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'delete')
def delete(call):
    bot.answer_callback_query(call.id)
    jsdata = json.loads(call.data)
    filename, action = jsdata['data'], jsdata['state']
    if action:
        os.remove(tools.unlex(filename))
    msg = explorer_func(filename[:filename.rfind('/')])
    bot.edit_message_text(text='your files', reply_markup=msg, chat_id=call.message.chat.id,
                          message_id=call.message.id)


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'close')
def close(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.delete_message(message_id=call.message.id, chat_id=call.message.chat.id)


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'].startswith('?'))
def conf_action(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    callback = json.loads(call.data)
    callback['handler'] = callback['handler'][1:]
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton('confirm✅', callback_data=json.dumps({**callback, "state": True})))
    markup.row(types.InlineKeyboardButton("cancel❌", callback_data=json.dumps({**callback, "state": False})))
    bot.edit_message_text(message_id=call.message.id, chat_id=call.message.chat.id, text="confirm action:",
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'upload')
def upload(call):
    path = json.loads(call.data)['data']
    bot.answer_callback_query(callback_query_id=call.id, text='send any file')
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, file_handler, call.message.id, path)
    pass


def file_handler(message, mid, path, target='new'):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    if message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        filename = file_info.file_path[file_info.file_path.rfind('/'):]
    elif message.video:
        file_info = bot.get_file(message.video.file_id)
        filename = message.video.file_name
    elif message.audio:
        file_info = bot.get_file(message.audio.file_id)
        filename = message.audio.file_name
    elif message.document:
        file_info = bot.get_file(message.document.file_id)
        filename = message.document.file_name
    else:
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(text='❌', callback_data='{"handler": "close"}'))
        bot.send_message(chat_id=message.chat.id, text='unsupported type', reply_markup=markup)
        return
    downloaded_file = bot.download_file(file_info.file_path)
    enc_path = tools.unlex(path)
    if target == 'replace':
        os.remove(enc_path)
        name = f'{enc_path[:enc_path.rfind(".")]}{filename[filename.rfind("."):]}'
    else:
        name = f"{enc_path}/{filename}"
    with open(name, 'wb') as new_file:
        new_file.write(downloaded_file)
    if target == 'new':
        msg = explorer_func(path)
        bot.edit_message_text(text='your files', reply_markup=msg, chat_id=message.chat.id, message_id=mid)
    else:
        fid = tools.lex(os.path.split(name)[1])
        file_view_func(f"{path[:path.rfind('/')]}/{fid}", message_id=mid, chat_id=message.chat.id)
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'replace')
def replace(call):
    path = json.loads(call.data)['data']
    bot.answer_callback_query(callback_query_id=call.id, text='send file')
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, file_handler, call.message.id, path, 'replace')


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'hardware_monitor')
def hardware_monitor(call):
    if not access(call.message):
        return
    mid = json.loads(call.data).get('data', None)
    if not mid:
        mid = bot.send_message(chat_id=call.message.chat.id, text='please, wait for result').id
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=mid, text='please, wait for result')
    result = tools.get_sensors()
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text='🔄',
                                          callback_data=json.dumps({"handler": "hardware_monitor", "data": mid})),
               types.InlineKeyboardButton(text='❌', callback_data='{"handler": "close"}'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=mid, text=result, reply_markup=markup)
    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'run')
def create_process(call):
    filename = json.loads(call.data)['data']
    process.Process(file=filename, absfile=os.path.abspath(tools.unlex(filename)),
                    default_dir=os.getcwd(), handler=bot)
    bot.answer_callback_query(text='process was started successfully', callback_query_id=call.id)


@bot.message_handler(content_types=['text', 'audio', 'photo', 'video', 'media', 'file', 'voice', 'video_note'])
def deleter(message):
    bot.delete_message(message.chat.id, message.id)


try:
    print('host created, dont shutdown your PC')
    bot.infinity_polling()
except:
    tools.reset_token()
