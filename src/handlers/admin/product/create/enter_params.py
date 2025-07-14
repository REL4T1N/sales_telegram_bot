from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.database import get_db
from database.models import Catalog, Category, Unit, Product

from states.admin.product.create_product import CreateProduct

from services.product.base import get_all, create_object

from services.product.create import get_categories_by_catalog

from utils.formatting_float_nums import pretty_num

from schemas.product import ProductCreate

from handlers.admin.base import IsAdmin

from keyboards.admin.base import create_keyboard, create_back_button, confirming_keyboard

from handlers.admin.product.create.catalog import show_categories_list, back_to_show_catalogs_list


async def kb_units_list():
    async for db in get_db():
        units = await get_all(db, Unit)

    kb = await create_keyboard(units, "Добавить", "add_new_unit", "back_to_enter_size")

    return kb


async def enter_size(mes: Message, state: FSMContext):
    try:
        size = float(mes.text.replace(",", "."))
        if size <= 0:
            raise ValueError
        
    except Exception:
        await mes.answer(text="Пожалуйства, введите неотрицательное число (≥ 0), <b><i>например,</i></b> <code>1.5</code>")
        return 
    
    await state.update_data(size=size)

    kb = await kb_units_list()

    await state.set_state(CreateProduct.choosing_unit)
    await mes.answer(
        text="Выберите единицу измерения товара или добавьте новую:",
        reply_markup=kb
    )


async def back_to_categories_list_on_size(query: CallbackQuery, state: FSMContext):
    if query.data == "back_to_categories_list":

        data = await state.get_data()
        await state.clear()
        await state.update_data(catalog_id=data["catalog_id"])
        await show_categories_list(query, state)
        return

    else:
        query.answer(text="Упс... Что-то пошло не так.\nПерезапустите приложение или свяжитесь с @REL4T1NCH1k")


async def enter_count(mes: Message, state: FSMContext):
    try:
        count = float(mes.text.replace(",", "."))
        if count <= 0 or count != int(count):
            raise ValueError
        
    except Exception:
        await mes.answer(text="Пожалуйства, введите целое неотрицательное число (≥ 0), <b><i>например,</i></b> <code>10</code>")
        return 
    
    kb = await create_back_button("back_to_enter_count")
    
    await state.update_data(count=count)
    await state.set_state(CreateProduct.entering_price)
    await mes.answer(
        text="Введите цену за одну единицу, <b><i>например,</i></b> <code>799.99</code>",
        reply_markup=kb
    )


async def back_to_units_on_count(query: CallbackQuery, state: FSMContext):
    if query.data == "back_to_units_list":
        data = await state.get_data()
        await state.clear()
        
        
        await state.update_data(catalog_id=data["catalog_id"])
        await state.update_data(category_id=data["category_id"])
        await state.update_data(size=data["size"])
        
        kb = await kb_units_list()

        await state.set_state(CreateProduct.choosing_unit)
        await query.message.answer(
            text="Выберите единицу измерения товара или добавьте новую:",
            reply_markup=kb
        )
        await query.answer()

    else:
        query.answer(text="Упс... Что-то пошло не так.\nПерезапустите приложение или свяжитесь с @REL4T1NCH1k")


async def enter_price(mes: Message, state: FSMContext):
    try:
        price = float(mes.text.replace(",", "."))
        if price <= 0:
            raise ValueError
        
    except Exception:
        await mes.answer(text="Пожалуйства, введите неотрицательное число, <b><i>например,</i></b> <code>799.99</code>")
        return 
    
    kb = await create_back_button("back_to_enter_price")
    
    await state.update_data(price=price)
    data = await state.get_data()

    kb = await confirming_keyboard("✅ Да", "add_product", "❌ Нет", "not_add_product")

    async for db in get_db():

        catalog = await db.get(Catalog, data["catalog_id"])
        category = await db.get(Category, data["category_id"])
        unit = await db.get(Unit, data["unit_id"])

        catalog_name = catalog.name if catalog else ""
        category_name = category.name if category else ""
        unit_name = unit.name if unit else ""

    text = (
            f"<b>Информация по продукту:</b>\n"
            f"<b>Каталог:</b> {catalog_name}\n"
            f"<b>Категория:</b> {category_name}\n"
            f"<b>Размер единицы продукции:</b> <i>{pretty_num(data['size'])}</i>\n"
            f"<b>Единица измерения:</b> {unit_name}\n"
            f"<b>Количество продукции:</b> <i>{pretty_num(data['count'])}</i> шт.\n"
            f"<b>Цена:</b> <i>{pretty_num(price)}</i>₽\n"
            f"<b>------</b>\n"
            f"<b>Добавить этот товар?</b>"
    )

    await state.set_state(CreateProduct.confirming)
    await mes.answer(
        text=text,
        reply_markup=kb
    ) 


# на случай добавления описания и фотографии
'''
async def enter_price(mes: Message, state: FSMContext):
    try:
        price = float(mes.text.replace(",", "."))
        if price <= 0:
            raise ValueError
        
    except Exception:
        await mes.answer(text="Пожалуйства, введите неотрицательное число, <b><i>например,</i></b> <code>799.99</code>")
        return 
    
    kb = await create_back_button("back_to_enter_price")
    
    await state.update_data(price=price)
    data = await state.get_data()

    kb = await confirming_keyboard("✅ Да", "add_desc", "❌ Нет", "not_add_desc")

    async for db in get_db():

        catalog = await db.get(Catalog, data["catalog_id"])
        category = await db.get(Category, data["category_id"])
        unit = await db.get(Unit, data["unit_id"])

        catalog_name = catalog.name if catalog else ""
        category_name = category.name if category else ""
        unit_name = unit.name if unit else ""

    text = (
            f"<b>Информация по продукту:</b>\n"
            f"<b>Каталог:</b> {catalog_name}\n"
            f"<b>Категория:</b> {category_name}\n"
            f"<b>Размер единицы продукции:</b> <i>{pretty_num(data['size'])}</i>\n"
            f"<b>Единица измерения:</b> {unit_name}\n"
            f"<b>Количество продукции:</b> <i>{pretty_num(data['count'])}</i> шт.\n"
            f"<b>Цена:</b> <i>{pretty_num(price)}</i>₽\n"
            f"<b>------</b>\n"
            f"<b>Добавить описание?</b>"
    )

    await state.set_state(CreateProduct.adding_desc)
    await mes.answer(
        text=text,
        reply_markup=kb
    )    
'''


async def back_to_count_on_price(query: CallbackQuery, state: FSMContext):
    if query.data == "back_to_enter_count":
        data = await state.get_data()
        await state.clear()
        
        
        await state.update_data(catalog_id=data["catalog_id"])
        await state.update_data(category_id=data["category_id"])
        await state.update_data(size=data["size"])
        await state.update_data(unit_id=data["unit_id"])
        
        kb = await create_back_button("back_to_units_list")

        await state.set_state(CreateProduct.entering_count)
        await query.message.answer(
            text="Введите доступное количество товара, <b><i>например,</i></b> <code>10</code>",
            reply_markup=kb
        )
        await query.answer()

    else:
        query.answer(text="Упс... Что-то пошло не так.\nПерезапустите приложение или свяжитесь с @REL4T1NCH1k")


async def confirm_add_product(query: CallbackQuery, state: FSMContext):
    if query.data == "add_product":
        data = await state.get_data()

        product_create = ProductCreate(
            category_id=data["category_id"],
            unit_id=data["unit_id"],
            available=True if data["count"] > 0 else False,
            size=data["size"],
            count=data["count"],
            price=data["price"]
        )

        async for db in get_db():
            product = await create_object(db, Product, **product_create.dict())

        await state.clear()
        await query.message.edit_text( # сделать переброс на отображение меню
            text="Нажмите /create_product, чтобы добавить ещё один товар"
        )
        await query.answer(text="✅ Товар успешно добавлен")
    
    elif query.data == "not_add_product":
        await state.clear()
        await query.answer(text="❌ Добавление товара отменено")
        await query.message.edit_text( # сделать переброс на отображение меню
            text="Нажмите /create_product, чтобы добавить ещё один товар"
        )

    else:
        query.answer(text="Упс... Что-то пошло не так.\nПерезапустите приложение или свяжитесь с @REL4T1NCH1k")
        



def register_product_create_enter_params(dp: Dispatcher):
    dp.message.register(enter_size, CreateProduct.entering_size, IsAdmin())
    dp.callback_query.register(back_to_categories_list_on_size, CreateProduct.entering_size, IsAdmin())
    dp.message.register(enter_count, CreateProduct.entering_count, IsAdmin())
    dp.callback_query.register(back_to_units_on_count, CreateProduct.entering_count, IsAdmin())
    dp.message.register(enter_price, CreateProduct.entering_price, IsAdmin())
    dp.callback_query.register(back_to_count_on_price, CreateProduct.entering_price, IsAdmin())
    dp.callback_query.register(confirm_add_product, CreateProduct.confirming, IsAdmin())