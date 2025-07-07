from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


work_with_catalog_buttons = [
    [
        InlineKeyboardButton(text="Отобразить список доступных категорий", callback_data="catalog_list")
    ],
    [
        InlineKeyboardButton(text="Добавить товар", callback_data="create_category")
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


back_to_catalog_button = [
    [
        InlineKeyboardButton(text="Назад", callback_data="back_to_catalog")
    ]
]

yes_or_cancel_buttons = [
    [
        InlineKeyboardButton(text="Да", callback_data="yes_create_product"),
        InlineKeyboardButton(text="Отмена", callback_data="cancel_create_product")
    ]
]

work_with_catalog_keyboard = InlineKeyboardMarkup(inline_keyboard=work_with_catalog_buttons)
back_to_catalog_keyboard = InlineKeyboardMarkup(inline_keyboard=back_to_catalog_button)
yes_or_cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=yes_or_cancel_buttons)