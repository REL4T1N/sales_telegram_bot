import asyncio

from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.filters import CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from sqlalchemy import select

from handlers.admin import IsAdmin, admin_ids

from database.database import get_db
from database.models import Unit, Product, Category, Catalog

from keyboards.common import create_keyboard

from services.product.common import create_object, update_object, get_all
from services.product.product import get_product_display_info

from states.product import UpdateProductStates

from utils.formatting_float_nums import pretty_num

def pad(text, width):
    """Заполняет пробелами до нужной ширины (слева и справа — чтобы центрировать)"""
    return f"{str(text):^{width}}"


# попробует отобразить весь список продуктов:
# async def show_products_list(query: CallbackQuery, state: FSMContext):
#     if query.data == "кнопка назад":
#         pass
#     else:
#         await state.update_data(category_id=int(query.data))
#         data = await state.get_data()
#         async for db in get_db():
#             products = await db.execute(
#                 select(Product).where(Product.category_id == data["category_id"])
#             )
#             products = products.scalars().all()

#             catalog = await db.get(Catalog, data["catalog_id"])
#             category = await db.get(Category, data["category_id"])
#             catalog_name = catalog.name if catalog else ""
#             category_name = category.name if category else ""

#             if not products:
#                 query.message.answer(f"Товары для {catalog_name} {category_name} не найдены")

async def show_products_list(query: CallbackQuery, state: FSMContext):
    if query.data == "кнопка назад":
        # обработка назад
        return
    else:
        await state.update_data(category_id=int(query.data))
        data = await state.get_data()
        async for db in get_db():
            products = await db.execute(
                select(Product).where(Product.category_id == data["category_id"])
            )
            products = products.scalars().all()

            catalog = await db.get(Catalog, data["catalog_id"])
            category = await db.get(Category, data["category_id"])
            catalog_name = catalog.name if catalog else ""
            category_name = category.name if category else ""

            if not products:
                await query.message.answer(f"Товары для {catalog_name} {category_name} не найдены")
                return

            # Ширина столбцов
            col_widths = [3, 10, 12, 10]
            # Заголовки
            header = f"{pad('№', col_widths[0])}|{pad('Размер', col_widths[1])}|{pad('Кол-во', col_widths[2])}|{pad('Цена', col_widths[3])}"
            sep = '-' * len(header)
            lines = [
                f"Каталог: {catalog_name}",
                f"Категория: {category_name}",
                "```",  # начало блока
                header,
                sep,
            ]
            buttons = []
            for idx, p in enumerate(products, 1):
                unit = await db.get(Unit, p.unit_id)
                unit_name = unit.name if unit else ""
                row = f"{pad(idx, col_widths[0])}|{pad(str(pretty_num(p.size)) + ' ' + unit_name, col_widths[1])}|{pad(pretty_num(p.quantity), col_widths[2])}|{pad(pretty_num(p.price), col_widths[3])}₽"
                lines.append(row)
                buttons.append([InlineKeyboardButton(text=str(idx), callback_data=f"{p.id}")])
            lines.append("```")  # конец блока
            # Кнопка назад
            buttons.append([InlineKeyboardButton(text="Назад(НЕ РАБОТАЕТ)", callback_data="back_to_choose_category")])

            kb = InlineKeyboardMarkup(inline_keyboard=buttons)
            await state.set_state(UpdateProductStates.choose_product_parametr_to_edit)
            await query.message.answer(
                text="\n".join(lines),
                reply_markup=kb,
                parse_mode="MarkdownV2"  # используем Markdown для моноширинного текста
            )
            await query.answer()

async def choose_product_paran_to_edit(query: CallbackQuery, state: FSMContext):
    if query.data == "back_to_choose_category":
        #заглушка для кнопки назад
        pass
    
    else:
        product_id = int(query.data)
        await state.update_data(product_id=product_id)
        data = await state.get_data()
        
        async for db in get_db():

            product = await db.get(Product, product_id)
            catalog = await db.get(Catalog, data["catalog_id"])
            category = await db.get(Category, data["category_id"])
            unit = await db.get(Unit, product.unit_id)

            catalog_name = catalog.name if catalog else ""
            category_name = category.name if category else ""
            unit_name = unit.name if unit else ""

        text = (
            f"<b>Информация по продукту</b>:\n"
            f"<b>Каталог</b>: {catalog_name}\n"
            f"<b>Категория</b>: {category_name}\n"
            f"<b>Размер единицы продукции</b>: <i>{pretty_num(product.size)}</i> {unit_name}\n"
            f"<b>Количество продукции</b>: <i>{pretty_num(product.quantity)}</i> штук\n"
            f"<b>Цена</b>: <i>{pretty_num(product.price)}₽</i>\n"
            f"<b>------</b>\n"
            f"<b>Выберите параметр для изменения:</b>"
        )

        buttons = [
            [
                InlineKeyboardButton(text="Размер", callback_data="size_one_product_edit"),
                InlineKeyboardButton(text="Единица измерения", callback_data="unit_product_edit")
            ],
            [
                InlineKeyboardButton(text="Количество продукции", callback_data="quantity_product_edit"),
                InlineKeyboardButton(text="Цена", callback_data="price_product_edit")
            ],
            [
                InlineKeyboardButton(text="Назад(НЕ РАБОТАЕТ)", callback_data="back_to_choose_product_to_edit")
            ]
        ]

        kb = InlineKeyboardMarkup(inline_keyboard=buttons)

        await state.set_state(UpdateProductStates.entering_product_parametr_to_edit)
        await query.message.answer(
            text=text,
            reply_markup=kb
        )
        await query.answer()


def register_update_product_handlers(dp: Dispatcher):
    dp.callback_query.register(show_products_list, UpdateProductStates.choose_category, IsAdmin())
    dp.callback_query.register(choose_product_paran_to_edit, UpdateProductStates.choose_product_parametr_to_edit, IsAdmin())