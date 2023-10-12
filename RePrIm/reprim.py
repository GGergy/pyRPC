import os
import json
import shutil
import telebot.apihelper
import multiprocessing
from io import BytesIO
from .util import tools, reprim_io
from .util.callback_io import call_out, io_override, lambda_generator
from telebot import types


tools.init()
bot = tools.load_bot()
main_function = None
__process = None


def access(message):
    if message.chat.id != tools.data['host']:
        bot.send_message(chat_id=message.chat.id, text='you have no access to this RPC')
    else:
        return True


@bot.message_handler(commands=['start'])
def start(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    bot.delete_message(message_id=message.id, chat_id=message.chat.id)
    tools.create_host(message.chat.id)
    if not access(message):
        return
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton('explorer',
                                          callback_data='{"handler": "explore", "data": ".", "new": true}'))
    markup.row(types.InlineKeyboardButton('start/stop project', callback_data='{"handler": "start"}'))
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
                                              callback_data=call_out(handler="explore", data=f"{path}/{folder[0]}")))
        buttons += 1
    for file in files:
        if buttons >= 45:
            break
        markup.row(types.InlineKeyboardButton(text=f'📄{file[1]}',
                                              callback_data=call_out(handler="selectfile", data=f"{path}/{file[0]}")))
        buttons += 1
    markup.row(types.InlineKeyboardButton(text='🔄', callback_data=call_out(handler="explore", data=path)),
               types.InlineKeyboardButton(text='console',
                                          callback_data=call_out(handler="console", data=path))
               )
    markup.row(types.InlineKeyboardButton(text='📤upload',
                                          callback_data=call_out(handler="upload", data=path)),
               types.InlineKeyboardButton(text='⬇️download',
                                          callback_data=call_out(handler="download_dir", data=path))
               )
    btns = []
    if path != '.':
        btns.append(types.InlineKeyboardButton(text='🔙', callback_data=call_out(handler="explore",
                                                                                data=os.path.split(path)[0])))
        if len(path.split('/')) > 2:
            btns.append(types.InlineKeyboardButton(text='🏠',  callback_data=call_out(handler="explore", data=".")))
    btns.append(types.InlineKeyboardButton(text='❌', callback_data=call_out(handler="close")))
    markup.row(*btns)
    return markup


@bot.callback_query_handler(lambda_generator('explore'))
@io_override
def handle_explorer(call, data, new=False):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    msg = explorer_func(data)
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


@bot.callback_query_handler(lambda_generator('selectfile'))
@io_override
def file_view(call, data):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    filename = data
    file_view_func(filename, call.message.id, call.message.chat.id)


def file_view_func(filename, message_id, chat_id):
    only_name = os.path.split(tools.unlex(filename))[1]
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text='⬇️download',
                                          callback_data=call_out(handler="download", data=filename)),
               types.InlineKeyboardButton(text='🗑️delete',
                                          callback_data=call_out(handler="?delete", data=filename)))
    markup.row(types.InlineKeyboardButton(text='✏️rename',
                                          callback_data=call_out(handler="rename", data=filename)),
               types.InlineKeyboardButton(text='🔄replace',
                                          callback_data=call_out(handler="replace", data=filename)))
    markup.row(types.InlineKeyboardButton(text='🔙', callback_data=call_out(handler="explore",
                                                                           data=os.path.dirname(filename))),
               types.InlineKeyboardButton(text='❌', callback_data=call_out(handler="close")))
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'selected file - {only_name}',
                          reply_markup=markup)


@bot.callback_query_handler(lambda_generator('download'))
@io_override
def download(call, data):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    filename = tools.unlex(data)
    with open(filename, mode='rb') as rf:
        data = BytesIO(rf.read())
        data.name = os.path.split(filename)[1]
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text='❌', callback_data=call_out('close')))
    try:
        bot.send_document(chat_id=call.message.chat.id, reply_markup=markup, document=data)
        bot.answer_callback_query(callback_query_id=call.id)
    except:
        bot.send_message(chat_id=call.message.chat.id, reply_markup=markup, text='file is empty or too much')


@bot.callback_query_handler(lambda_generator('delete'))
@io_override
def delete(call, data, state):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.answer_callback_query(call.id)
    filename, action = data, state
    if action:
        os.remove(tools.unlex(filename))
    msg = explorer_func(filename[:filename.rfind('/')])
    bot.edit_message_text(text='your files', reply_markup=msg, chat_id=call.message.chat.id,
                          message_id=call.message.id)


@bot.callback_query_handler(lambda_generator('close'))
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


@bot.callback_query_handler(lambda_generator('upload'))
@io_override
def upload(call, data):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    path = data
    bot.answer_callback_query(callback_query_id=call.id, text='send any file')
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, file_handler, call.message.id, path)
    pass


def file_handler(message, mid, path, target='new'):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
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


@bot.callback_query_handler(lambda_generator('replace'))
@io_override
def replace(call, data):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    path = data
    bot.answer_callback_query(callback_query_id=call.id, text='send file')
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, file_handler, call.message.id, path, 'replace')


@bot.callback_query_handler(lambda_generator('hardware_monitor'))
@io_override
def hardware_monitor(call, mid=None):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    if not mid:
        mid = bot.send_message(chat_id=call.message.chat.id, text='please, wait for result').id
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=mid, text='please, wait for result')
    result = tools.get_sensors()
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text='🔄',
                                          callback_data=call_out(handler="hardware_monitor", mid=mid)),
               types.InlineKeyboardButton(text='❌', callback_data=call_out('close')))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=mid, text=result, reply_markup=markup)
    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(lambda_generator('console'))
@io_override
def create_console(call, data):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    file = data
    bot.answer_callback_query(text='send command', callback_query_id=call.id)
    bot.register_next_step_handler_by_chat_id(chat_id=call.message.chat.id, callback=console_handler,
                                              file=tools.unlex(file))


def console_handler(message, file):
    mk = types.InlineKeyboardMarkup()
    mk.row(types.InlineKeyboardButton('❌', callback_data=call_out('close')))
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    bot.send_message(text=tools.execute_command(message.text, file), chat_id=message.chat.id, reply_markup=mk)


@bot.callback_query_handler(lambda_generator('download_dir'))
@io_override
def download_dir(call, data):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.answer_callback_query(callback_query_id=call.id, text='building zip file...')
    path = tools.unlex(data)
    chat_id = call.message.chat.id
    archive = shutil.make_archive('buff', 'zip', path)
    with open(archive, mode='rb') as rf:
        data = BytesIO(rf.read())
        data.name = f'{path.split("//")[-1]}.zip'
        if data.name == '..zip':
            data.name = 'source.zip'
    os.remove('buff.zip')
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text='❌', callback_data='{"handler": "close"}'))
    send(blob=data, chat_id=chat_id, mk=markup)


def send(chat_id, blob, mk):
    try:
        bot.send_document(chat_id=chat_id, document=blob, reply_markup=mk)
    except:
        bot.send_message(chat_id=chat_id, text="cannot send zip file, it's too much", reply_markup=mk)


@bot.callback_query_handler(lambda_generator('rename'))
@io_override
def rename_file(call, data):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    file = data
    bot.answer_callback_query(callback_query_id=call.id, text='send new filename')
    bot.register_next_step_handler_by_chat_id(chat_id=call.message.chat.id, callback=handler_filename, old=file,
                                              call=call)


def handler_filename(message, old, call):
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    new_name = message.text
    unlex = tools.unlex(old)
    dirname = os.path.dirname(unlex)
    rs = unlex[unlex.rfind('.'):]
    new_path = f'{dirname}/{new_name}{rs}'
    os.renames(tools.unlex(old), new_path)
    fid = tools.lex(f'{new_name}{rs}')
    file_view_func(message_id=call.message.id, chat_id=call.message.chat.id,
                   filename=old[:old.rfind('/') + 1] + str(fid))


@bot.callback_query_handler(lambda_generator('start'))
@io_override
def start_project(call):
    global __process

    if not main_function:
        bot.answer_callback_query(callback_query_id=call.id, text='Main function is not configured')
        return
    if not __process.is_alive():
        __process.start()
        bot.answer_callback_query(callback_query_id=call.id, text='Project started')
        return
    __process.terminate()
    __process.close()
    __process = multiprocessing.Process(target=main_function)
    bot.answer_callback_query(callback_query_id=call.id, text='Project stopped')


@bot.message_handler(content_types=['text', 'audio', 'photo', 'video', 'media', 'file', 'voice', 'video_note'])
def deleter(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    bot.delete_message(message.chat.id, message.id)
    with open('.rtmp', 'w') as f:
        f.write(message.text)


def config(main_func, prestart=False):
    global main_function, __process
    main_function = main_func
    __process = multiprocessing.Process(target=main_function)
    if prestart:
        __process.start()


def get_io_clients():
    return reprim_io.RePrImInput(handler=bot), reprim_io.RePrImOutput(handler=bot)


def start_host():
    try:
        print("successfully started RePrIm 0.1.4 by GGergy (https://github.com/GGergy/)")
        print('host created, dont shutdown your PC')
        if not main_function:
            print('Warning: main function is not configured, project cannot run')
        bot.infinity_polling()
    except:
        tools.reset_token()
