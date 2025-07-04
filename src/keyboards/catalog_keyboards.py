from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


catalog_buttons = [
    [InlineKeyboardButton(text="Варенье", callback_data="jam")],
    [InlineKeyboardButton(text="Компоты", callback_data="compote")],
    [InlineKeyboardButton(text="Салаты", callback_data="salad")],
    [InlineKeyboardButton(text="Соленья", callback_data="pickle")]
]

jam_buttons = [
    [InlineKeyboardButton(text="Сливовое", callback_data="jam_plum")]
    [InlineKeyboardButton(text="Вишневое", callback_data="jam_cherry")]
    [InlineKeyboardButton(text="Абрикосовое", callback_data="jam_apricot")]
    [InlineKeyboardButton(text="Назад", callback_data="catalog_menu")]
]

compote_buttons = [
    [InlineKeyboardButton(text="Сливовый", callback_data="compote_plum")]
    [InlineKeyboardButton(text="Вишневый", callback_data="compote_cherry")]
    [InlineKeyboardButton(text="Абрикосовый", callback_data="compote_apricot")]
    [InlineKeyboardButton(text="Назад", callback_data="catalog_menu")]
]

salad_buttons = [
    [InlineKeyboardButton(text="Икра", callback_data="salad_ikra")]
    [InlineKeyboardButton(text="Перец", callback_data="salad_perec")]
    [InlineKeyboardButton(text="Свекровь", callback_data="salad_svecrov")]
    [InlineKeyboardButton(text="Назад", callback_data="catalog_menu")]
]

catalog_keyboard = InlineKeyboardMarkup(inline_keyboard=catalog_buttons)
jam_keyboard = InlineKeyboardMarkup(inline_keyboard=jam_buttons)
compote_keyboard = InlineKeyboardMarkup(inline_keyboard=compote_buttons)
salad_keyboard = InlineKeyboardMarkup(inline_keyboard=salad_buttons)
