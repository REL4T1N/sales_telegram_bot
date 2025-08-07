from typing import List, Optional

from aiogram.types import CallbackQuery, Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from database.models import Product, Unit, Catalog, Category

from states.admin.product.update_product import UpdateProduct

from keyboards.admin.product.update_product import generate_product_edit_keyboard

from utils.formatting_float_nums import pad, pretty_num
from utils.product_utils import generate_product_info_text

from services.product.update.base import update_object


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


async def handle_param_input(param_type: str, mes: Message, state: FSMContext):
    """Обрабатывает ввод параметров продукта (size, count, price)."""
    param_map = {
        "size": {"state_key": "new_size", "parse_func": float, "error_msg": "Пожалуйста, введите неотрицательное число, например, 1.5"},
        "count": {"state_key": "new_count", "parse_func": lambda x: int(float(x)), "error_msg": "Пожалуйста, введите целое неотрицательное число, например, 10"},
        "price": {"state_key": "new_price", "parse_func": float, "error_msg": "Пожалуйста, введите неотрицательное число, например, 799.99"}
    }
    
    try:
        value = mes.text.replace(",", ".")
        parsed_value = param_map[param_type]["parse_func"](value)
        if parsed_value < 0 or (param_type == "count" and parsed_value != int(parsed_value)):
            raise ValueError
    except Exception:
        await mes.answer(text=param_map[param_type]["error_msg"])
        return
    
    await state.update_data(**{param_map[param_type]["state_key"]: parsed_value})
    data = await state.get_data()
    
    async for db in get_db():
        product = await db.get(Product, data["product_id"])
        text, flag = await generate_product_info_text(db, product, data)
    
    kb = await generate_product_edit_keyboard(flag)
    await state.set_state(UpdateProduct.choosing_product_parametr)
    await mes.answer(text=text, reply_markup=kb)


async def confirm_changes(query: CallbackQuery, state: FSMContext):
    """Подтверждает изменения параметров продукта."""
    data = await state.get_data()
    fields_to_update = {param: data[f"new_{param}"] for param in ("size", "count", "price", "unit_id") if f"new_{param}" in data and data[f"new_{param}"] is not None}
    
    await state.clear()
    await state.update_data(catalog_id=data["catalog_id"], category_id=data["category_id"])
    
    if fields_to_update:
        async for db in get_db():
            await update_object(db, Product, obj_id=data["product_id"], **fields_to_update)
        await display_products_list(query, state, start_text="✅ Товар успешно обновлён")
    else:
        await display_products_list(query, state, start_text="Нет новых изменений для сохранения")


async def cancel_changes(query: CallbackQuery, state: FSMContext):
    """Отменяет изменения параметров продукта."""
    data = await state.get_data()
    await state.clear()
    await state.update_data(catalog_id=data["catalog_id"], category_id=data["category_id"])
    await display_products_list(query, state, start_text="Изменения отменены")