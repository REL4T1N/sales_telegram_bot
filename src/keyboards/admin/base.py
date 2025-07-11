from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def create_keyboard(objects, add_text, add_callback, add_back_callback):
    buttons = []
    i = 0
    while i < len(objects):
        # Если это последний элемент и всего объектов нечетное количество
        if i == len(objects) - 1 and len(objects) % 2 == 1:
            row = [
                InlineKeyboardButton(text=objects[i].name, callback_data=str(objects[i].id)),
                InlineKeyboardButton(text=add_text, callback_data=add_callback)
            ]
            buttons.append(row)
            break
        else:
            row = [
                InlineKeyboardButton(text=objects[i].name, callback_data=str(objects[i].id)),
                InlineKeyboardButton(text=objects[i+1].name, callback_data=str(objects[i+1].id))
            ]
            buttons.append(row)
            i += 2
    # Если объектов чётное количество, кнопку "Добавить" на отдельную строку
    if len(objects) % 2 == 0:
        buttons.append([
            InlineKeyboardButton(text=add_text, callback_data=add_callback)
        ])
    # Кнопка "Назад" всегда на новой строке
    buttons.append([
        InlineKeyboardButton(text="Назад", callback_data=add_back_callback)
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def create_back_button(data: str):
    button = [
        [
            InlineKeyboardButton(text="Назад", callback_data=data)
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=button)


async def confirming_keyboard(confirm_text: str, confirm_callback: str, cancel_text: str, cancel_callback: str):
    buttons = [
        [
            InlineKeyboardButton(text=confirm_text, callback_data=confirm_callback),
            InlineKeyboardButton(text=cancel_text, callback_data=cancel_callback)
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)