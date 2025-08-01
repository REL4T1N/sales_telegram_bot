from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


catalog_action_buttons = [
    [
        InlineKeyboardButton(text="Изменить название", callback_data="update_catalog_name"), 
    ],
    [
        InlineKeyboardButton(text="Не изменять название", callback_data="cancel_update_catalog_name"),
    ],
    [
        InlineKeyboardButton(text="Назад(НЕ РАБОТАЕТ)", callback_data="back_to_main_product_menu")
    ]
]

category_action_buttons = [
    [
        InlineKeyboardButton(text="Изменить название", callback_data="update_category_name"), 
    ],
    [
        InlineKeyboardButton(text="Не изменять название", callback_data="cancel_update_category_name"),
    ],
    [
        InlineKeyboardButton(text="Назад(РАБОТАЕТ)", callback_data="back_to_choose_catalog_for_category")
    ]
]

catalog_action_kb = InlineKeyboardMarkup(inline_keyboard=catalog_action_buttons)
category_action_kb = InlineKeyboardMarkup(inline_keyboard=category_action_buttons)