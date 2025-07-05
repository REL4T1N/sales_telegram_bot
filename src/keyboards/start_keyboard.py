from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


start_admin_buttons = [
    [
        KeyboardButton(text="Каталог"),
        KeyboardButton(text="Обновить каталог")
    ],
    [
        KeyboardButton(text="О нас"),
        KeyboardButton(text="Тех. Поддержка"),
    ]
]

start_buttons = [
    [
        KeyboardButton(text="Каталог"),
        KeyboardButton(text="Заказы"),
    ],
    [
        KeyboardButton(text="О нас"),
        KeyboardButton(text="Тех. Поддержка"),
    ]
]

start_admin_keyboard = ReplyKeyboardMarkup(keyboard=start_admin_buttons, resize_keyboard=True)
start_keyboard = ReplyKeyboardMarkup(keyboard=start_buttons, resize_keyboard=True)