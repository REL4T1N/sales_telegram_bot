from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Product, Unit, Catalog, Category

from utils.formatting_float_nums import pad, pretty_num, pretty_edit

async def generate_products_table(
    db: AsyncSession,
    products: List[Product],
    catalog_name: str,
    category_name: str,
    buttons_per_row: int = 2
) -> tuple[str, InlineKeyboardMarkup]:
    """
    Генерирует текстовую таблицу продуктов и клавиатуру с кнопками.
    
    Args:
        db: Асинхронная сессия базы данных
        products: Список продуктов
        catalog_name: Название каталога
        category_name: Название категории
        buttons_per_row: Количество кнопок в строке
    
    Returns:
        Кортеж: (текст таблицы в Markdown, объект InlineKeyboardMarkup)
    """
    col_widths = [3, 10, 12, 10]
    header = f"{pad('№', col_widths[0])}|{pad('Размер', col_widths[1])}|{pad('Кол-во', col_widths[2])}|{pad('Цена', col_widths[3])}"
    sep = '-' * len(header)
    lines = [
        f"Каталог: {catalog_name}",
        f"Категория: {category_name}",
        "```",
        header,
        sep,
    ]

    buttons = []
    temp_row = []

    for idx, p in enumerate(products, 1):
        unit = await db.get(Unit, p.unit_id)
        unit_name = unit.name if unit else ""
        row = f"{pad(idx, col_widths[0])}|{pad(str(pretty_num(p.size)) + ' ' + unit_name, col_widths[1])}|{pad(pretty_num(p.count), col_widths[2])}|{pad(pretty_num(p.price), col_widths[3])}₽"
        lines.append(row)

        button = InlineKeyboardButton(text=str(idx), callback_data=f"{p.id}")
        temp_row.append(button)

        if len(temp_row) == buttons_per_row:
            buttons.append(temp_row)
            temp_row = []

    if temp_row:
        buttons.append(temp_row)

    buttons.append([InlineKeyboardButton(text="Назад(НЕ РАБОТАЕТ)", callback_data="back_to_choose_category")])
    lines.append("```")

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return "\n".join(lines), kb