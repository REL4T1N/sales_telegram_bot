from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def create_keyboard(objects, add_text, add_callback):
    buttons = []
    for i in range(0, len(objects), 2):
        row = []
        row.append(InlineKeyboardButton(text=objects[i].name, callback_data=str(objects[i].id)))
        if i + 1 < len(objects):
            row.append(InlineKeyboardButton(text=objects[i+1].name, callback_data=str(objects[i+1].id)))
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton(
            text=add_text,
            callback_data=add_callback
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)