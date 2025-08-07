from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Product, Unit, Catalog, Category

from utils.formatting_float_nums import pad, pretty_num, pretty_edit

from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Product, Category, Catalog
from database.database import get_db
from services.product.base import get_product_display_info
from states.admin.product.update_product import UpdateProduct


async def generate_products_table(
    db: AsyncSession,
    products: List[Product],
    catalog_name: str,
    category_name: str,
    start_text: Optional[str] = None, 
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
    lines = []
    
    # Добавляем стартовый текст, если он передан
    if start_text is not None:
        lines.append(start_text)
        lines.append("")  # Добавляем пустую строку для переноса

    lines.extend([
        f"Каталог: {catalog_name}",
        f"Категория: {category_name}",
        "```",
        header,
        sep,
    ])

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

    buttons.append([InlineKeyboardButton(text="Назад", callback_data="back_to_choose_category")])
    lines.append("```")

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return "\n".join(lines), kb


async def display_products_list(query: CallbackQuery, state: FSMContext, start_text: Optional[str] = None):
    data = await state.get_data()
    category_id = data.get("category_id")
    if not category_id:
        await query.message.answer("Категория не выбрана.")
        return

    async for db in get_db():
        products = await db.execute(
            select(Product).where(Product.category_id == category_id)
        )
        products = products.scalars().all()

        category = await db.get(Category, category_id)
        catalog = await db.get(Catalog, category.catalog_id)
        catalog_name = catalog.name if catalog else ""
        category_name = category.name if category else ""

        if not products:
            await query.message.answer(f"Товары для {catalog_name} {category_name} не найдены")
            return

        text, kb = await generate_products_table(
            db=db,
            products=products,
            catalog_name=catalog_name,
            category_name=category_name,
            start_text=start_text,
            buttons_per_row=3
        )

        await state.set_state(UpdateProduct.choosing_product)
        await query.message.edit_text(
            text=text,
            reply_markup=kb,
            parse_mode="MarkdownV2"
        )
        await query.answer()