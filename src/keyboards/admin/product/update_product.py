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
        InlineKeyboardButton(text="Назад", callback_data="back_to_choose_catalog_for_category")
    ]
]

catalog_action_kb = InlineKeyboardMarkup(inline_keyboard=catalog_action_buttons)
category_action_kb = InlineKeyboardMarkup(inline_keyboard=category_action_buttons)


async def generate_product_edit_keyboard(show_confirm_cancel: bool = False) -> InlineKeyboardMarkup:
    """
    Генерирует клавиатуру для редактирования параметров продукта.
    
    Args:
        show_confirm_cancel: Если True, добавляет кнопки "Подтвердить" и "Отменить"
    
    Returns:
        InlineKeyboardMarkup с кнопками
    """
    buttons = [
        [
            InlineKeyboardButton(text="Размер", callback_data="update_param:size"),
            InlineKeyboardButton(text="Единица измерения", callback_data="update_param:unit")
        ],
        [
            InlineKeyboardButton(text="Количество продукции", callback_data="update_param:count"),
            InlineKeyboardButton(text="Цена", callback_data="update_param:price")
        ]
    ]

    
    if show_confirm_cancel:
        buttons.append([
            InlineKeyboardButton(text="Подтвердить изменения", callback_data="confirm_param_update"),
            InlineKeyboardButton(text="Отменить изменения", callback_data="cancel_param_update")
        ])
    else:
        buttons.append([
            InlineKeyboardButton(text="Назад", callback_data="back_to_choose_product_to_update")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)