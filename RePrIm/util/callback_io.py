import json


def io_override(func):

    def wrapper(call):
        data = json.loads(call.data)
        data.pop('handler')
        return func(call, **data)

    return wrapper


# Генератор функции для отбора события кнопки под функцию
def lambda_generator(handler):
    return lambda call: json.loads(call.data)['handler'] == handler


# Энкодер данных для callback_data кнопки
def call_out(handler: str, **kwargs) -> str:
    """Creates a json string for button's callback data
    Usage:
    callback = call_out(handler='handler name', arg1=1, arg2='abcd', arg3=[1, 2, 3])
    button = types.InlineKeyboardButton(text="button text", callback_data=callback)
    :param handler:
    required parameter, needs to definitions of the processing function
    :param kwargs:
    optional parameters, can be any json-serializable types, but type Dict() may bug
    """
    kwargs['handler'] = handler
    return json.dumps(kwargs)
