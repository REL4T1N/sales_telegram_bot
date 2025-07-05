from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


work_with_catalog_buttons = [
    [
        InlineKeyboardButton(text="Отобразить список доступных категорий", callback_data="catalog_list")
    ],
    [
        InlineKeyboardButton(text="Добавить категорию", callback_data="create_category")
    ],
    [
        InlineKeyboardButton(text="Обновить категорию", callback_data="update_category")
    ],
    [
        InlineKeyboardButton(text="Удалеть категорию", callback_data="delete_category")
    ],
    [
        InlineKeyboardButton(text="Назад", callback_data="start_keyboard")
    ]
]

work_with_catalog_keyboard = InlineKeyboardMarkup(inline_keyboard=work_with_catalog_buttons)