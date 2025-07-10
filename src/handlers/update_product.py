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

from utils.formatting_float_nums import pretty_num, pretty_edit

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
            f"<b>Информация по продукту:</b>\n"
            f"<b>Каталог:</b> {catalog_name}\n"
            f"<b>Категория:</b> {category_name}\n"
            f"<b>Размер единицы продукции:</b> <i>{pretty_num(product.size)}</i>\n"
            f"<b>Единица измерения:</b> {unit_name}\n"
            f"<b>Количество продукции:</b> <i>{pretty_num(product.quantity)}</i> шт.\n"
            f"<b>Цена:</b> <i>{pretty_num(product.price)}</i>₽\n"
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


async def enter_product_parametr_to_edit(query: CallbackQuery, state: FSMContext):    
    if query.data == "back_to_choose_product_to_edit":
        # заглушка кнопки назад
        pass
    elif query.data == "end_param_edit":
        # заглушка для вызова меню подтверждения
        pass

    if query.data == "size_one_product_edit":
        await state.update_data(parametr="size")
        await state.set_state(UpdateProductStates.entering_new_size)
        await query.message.answer(
            text="Введите новое значение единицы продукции:"
        )
        await query.answer()

    elif query.data == "unit_product_edit":
        await state.update_data(parametr="unit")
        await state.set_state(UpdateProductStates.choose_new_unit)
        await query.message.answer(
            text="Выберите новую единицу измерения:",
            # отобразить клаву всех unit из БД
            # reply_markup=kb
        )
        await query.answer()

    elif query.data == "quantity_product_edit":
        await state.update_data(parametr="quantity")
        await state.set_state(UpdateProductStates.entering_new_quantity)
        await query.message.answer(
            text="Введите новое количество продукции:"
        )
        await query.answer()

    elif query.data == "price_product_edit":
        await state.update_data(parametr="price")
        await state.set_state(UpdateProductStates.entering_new_price)
        await query.message.answer(
            text="Введите новую цену за единицу продукции:"
        )
        await query.answer()

    else:
        query.answer("Что-то пошло не так")


async def enter_new_size(mes: Message, state: FSMContext):
    try:
        new_size = float(mes.text.replace(",", "."))
        if new_size <= 0:
            raise ValueError
        
    except Exception:
        await mes.answer(text="Пожалуйства, введите неотрицательное число, <b><i>например,</i></b> <code>1.5</code>")
        return 
    
    await state.update_data(new_size=new_size)
    
    buttons = [
        [
            InlineKeyboardButton(text="Продолжить изменения", callback_data="continue_param_edit"),
            InlineKeyboardButton(text="Закончить изменения", callback_data="end_param_edit")
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    # состояние выбора действия редактирования параметра
    await state.set_state(UpdateProductStates.choose_param_edit_action)
    await mes.answer(
        text="Выберите действие:",
        reply_markup=kb
    )


async def choose_new_unit(query: CallbackQuery, state: FSMContext):
    # пока нет вывода клавы - делать нет смысла
    pass

async def enter_new_quantity(mes: Message, state: FSMContext):
    try:
        new_quantity = float(mes.text.replace(",", "."))
        if new_quantity <= 0:
            raise ValueError
        
    except Exception:
        await mes.answer(text="Пожалуйства, введите неотрицательное число, <b><i>например,</i></b> <code>1.5</code>")
        return
    
    await state.update_data(new_quantity=new_quantity)
    
    buttons = [
        [
            InlineKeyboardButton(text="Продолжить изменения", callback_data="continue_param_edit"),
            InlineKeyboardButton(text="Закончить изменения", callback_data="end_param_edit")
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    # состояние выбора действия редактирования параметра
    await state.set_state(UpdateProductStates.choose_param_edit_action)
    await mes.answer(
        text="Выберите действие:",
        reply_markup=kb
    )


async def enter_new_price(mes: Message, state: FSMContext):
    try:
        new_price = float(mes.text.replace(",", "."))
        if new_price <= 0:
            raise ValueError
        
    except Exception:
        await mes.answer(text="Пожалуйства, введите неотрицательное число, <b><i>например,</i></b> <code>1.5</code>")
        return
    
    await state.update_data(new_price=new_price)
    
    buttons = [
        [
            InlineKeyboardButton(text="Продолжить изменения", callback_data="continue_param_edit"),
            InlineKeyboardButton(text="Закончить изменения", callback_data="end_param_edit")
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    # состояние выбора действия редактирования параметра
    await state.set_state(UpdateProductStates.choose_param_edit_action)
    await mes.answer(
        text="Выберите действие:",
        reply_markup=kb
    )


async def new_show_product(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    async for db in get_db():

        product = await db.get(Product, data["product_id"])
        catalog = await db.get(Catalog, data["catalog_id"])
        category = await db.get(Category, data["category_id"])
        unit = await db.get(Unit, product.unit_id)

        # new_unit_name = data.get("new_unit_name")
        # new_unit_id = data.get("new_unit_id")

        catalog_name = catalog.name if catalog else ""
        category_name = category.name if category else ""
        unit_name = unit.name if unit else ""

        size_str = pretty_edit(product.size, data.get("new_size"))
        quantity_str = pretty_edit(product.quantity, data.get("new_quantity"), " шт.")
        price_str = pretty_edit(product.price, data.get("new_price"), "₽")

    text = (
        f"<b>Информация по продукту:</b>\n"
        f"<b>Каталог:</b> {catalog_name}\n"
        f"<b>Категория:</b> {category_name}\n"
        f"<b>Размер единицы продукции:</b> {size_str}\n"
        f"<b>Единица измерения:</b> {unit_name}\n"
        f"<b>Количество продукции:</b> {quantity_str}\n"
        f"<b>Цена:</b> {price_str}\n"
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
            InlineKeyboardButton(text="Закончить изменения", callback_data="end_param_edit")
        ]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await state.set_state(UpdateProductStates.entering_product_parametr_to_edit)
    await query.message.answer(
        text=text,
        reply_markup=kb
    )
    await query.answer()


async def choose_param_edit_action(query: CallbackQuery, state: FSMContext):
    if query.data == "continue_param_edit":
        await new_show_product(query, state)
        await query.answer()

    elif query.data == "end_param_edit":
        data = await state.get_data()
        async for db in get_db():

            product = await db.get(Product, data["product_id"])
            catalog = await db.get(Catalog, data["catalog_id"])
            category = await db.get(Category, data["category_id"])
            unit = await db.get(Unit, product.unit_id)

            # new_unit_name = data.get("new_unit_name")
            # new_unit_id = data.get("new_unit_id")

            catalog_name = catalog.name if catalog else ""
            category_name = category.name if category else ""
            unit_name = unit.name if unit else ""

            size_str = pretty_edit(product.size, data.get("new_size"))
            quantity_str = pretty_edit(product.quantity, data.get("new_quantity"), " шт.")
            price_str = pretty_edit(product.price, data.get("new_price"), "₽")

        text = (
            f"<b>Информация по продукту:</b>\n"
            f"<b>Каталог:</b> {catalog_name}\n"
            f"<b>Категория:</b> {category_name}\n"
            f"<b>Размер единицы продукции:</b> {size_str}\n"
            f"<b>Единица измерения:</b> {unit_name}\n"
            f"<b>Количество продукции:</b> {quantity_str}\n"
            f"<b>Цена:</b> {price_str}\n"
            f"<b>------</b>\n"
            f"<b>Выберите действие:</b>"
        )

        buttons = [
            [
                InlineKeyboardButton(text="Подтвердить изменения", callback_data="confirm_param_edit"),
                InlineKeyboardButton(text="Отменить изменения", callback_data="cancel_param_edit")
            ]
        ]
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await state.set_state(UpdateProductStates.confirming_product_edit)
        await query.message.answer(
            text=text,
            reply_markup=kb
        )
        await query.answer()

    else:
        query.answer("Что-то пошло не так")


async def send_products_table(query: CallbackQuery, state: FSMContext, catalog_id: int, category_id: int):
    async for db in get_db():
        products = await db.execute(
            select(Product).where(Product.category_id == category_id)
        )
        products = products.scalars().all()

        catalog = await db.get(Catalog, catalog_id)
        category = await db.get(Category, category_id)
        catalog_name = catalog.name if catalog else ""
        category_name = category.name if category else ""

        if not products:
            await query.message.answer(text=f"Товары для {catalog_name} {category_name} не найдены")
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
            parse_mode="MarkdownV2"
        )
        await query.answer()


async def confirm_params_edit(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if query.data == "confirm_param_edit":
        fields_to_update = {}
        for param in ("size", "quantity", "price", "unit_id"):
            new_key = f"new_{param}"
            if new_key in data and data[new_key] is not None:
                fields_to_update[param] = data[new_key]
        
        if fields_to_update:
            async for db in get_db():
                product = await update_object(db, Product, obj_id=data["product_id"], **fields_to_update)
            await query.message.answer("✅ Товар успешно обновлён!")
        else:
            await query.message.answer("Нет новых изменений для сохранения.")

        await state.clear()
        await state.update_data(catalog_id=data["catalog_id"])
        await state.update_data(category_id=data["category_id"])
        await send_products_table(query, state, int(data["catalog_id"]), int(data["category_id"]))
        await query.answer()
        # сделать перенаправление на меню, где таблица в формате <code></code>

    elif query.data == "cancel_param_edit":
        await query.message.answer("Обновление отменено!")

    else:
        query.answer("Что-то пошло не так")



def register_update_product_handlers(dp: Dispatcher):
    dp.callback_query.register(show_products_list, UpdateProductStates.choose_category, IsAdmin())
    dp.callback_query.register(choose_product_paran_to_edit, UpdateProductStates.choose_product_parametr_to_edit, IsAdmin())
    dp.callback_query.register(enter_product_parametr_to_edit, UpdateProductStates.entering_product_parametr_to_edit, IsAdmin())
    dp.message.register(enter_new_size, UpdateProductStates.entering_new_size, IsAdmin())
    dp.callback_query.register(choose_new_unit, UpdateProductStates.choose_new_unit, IsAdmin())
    dp.message.register(enter_new_quantity, UpdateProductStates.entering_new_quantity, IsAdmin())
    dp.message.register(enter_new_price, UpdateProductStates.entering_new_price, IsAdmin())
    dp.callback_query.register(choose_param_edit_action, UpdateProductStates.choose_param_edit_action, IsAdmin())
    dp.callback_query.register(confirm_params_edit, UpdateProductStates.confirming_product_edit, IsAdmin())