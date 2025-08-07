import asyncio

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from sqlalchemy import select

from database.database import get_db
from database.models import Catalog, Category, Product, Unit

from states.admin.product.update_product import UpdateProduct

from services.product.base import get_all, get_categories_by_catalog, get_product_display_data, get_product_display_info

from services.product.create import create_object
from services.product.update.base import update_object

from handlers.admin.base import IsAdmin

from keyboards.admin.base import create_keyboard, create_back_button, confirming_keyboard
from keyboards.admin.product.update_product import catalog_action_kb, generate_product_edit_keyboard

from services.product.update.catalog import display_catalog_action_menu_for_update, display_catalogs_list_for_update
from services.product.update.category import display_category_action_menu_for_update, display_category_list_for_update
from services.product.update.block_params import generate_products_table, display_products_list


from utils.formatting_float_nums import pad, pretty_num, pretty_edit
from utils.product_utils import generate_product_info_text

admin_update_block_params = Router()

admin_update_block_params.message.filter(IsAdmin())
admin_update_block_params.callback_query.filter(IsAdmin())


@admin_update_block_params.callback_query(UpdateProduct.choosing_category_for_blocks)
async def show_blocks_list(query: CallbackQuery, state: FSMContext):
    if query.data == "back_update_choose_category_action":
        await display_category_action_menu_for_update(query, state)

    else:
        category_id = int(query.data)
        await state.update_data(category_id=category_id)
        await display_products_list(query, state)


@admin_update_block_params.callback_query(UpdateProduct.choosing_product)
async def choose_product_to_update(query: CallbackQuery, state: FSMContext):
    if query.data == "back_to_choose_category":
        await display_category_list_for_update(
            query,
            state,
            UpdateProduct.choosing_category_for_blocks,
            text="Выберите категорию:",
            clear_state=True
        )

    else:
        product_id = int(query.data)
        await state.update_data(product_id=product_id)
        
        async for db in get_db():
            product = await db.get(Product, product_id)
            text, flag = await generate_product_info_text(db, product)

        kb = await generate_product_edit_keyboard(flag)

        await state.set_state(UpdateProduct.choosing_product_parametr)
        await query.message.edit_text(
            text=text,
            reply_markup=kb
        )
        await query.answer()


@admin_update_block_params.callback_query(UpdateProduct.choosing_product_parametr)
async def choose_product_param_to_update(query: CallbackQuery, state: FSMContext):
    if query.data.startswith("update_param:"):
        param = query.data.split(":")[1]

        if param == "size":
            await state.set_state(UpdateProduct.entering_new_size)
            await query.message.edit_text(text="Введите новый размер одной единицы товара, <b><i>например,</i></b> <code>1.5</code>")

        elif param == "unit":
            await state.set_state(UpdateProduct.choosing_new_unit)
            async for db in get_db():
                units = await get_all(db, Unit)

            kb = await create_keyboard(units, "Добавить", "add_new_unit", "back_to_сhoose_unit_for_update")
            await state.set_state(UpdateProduct.choosing_new_unit)

            await query.message.edit_text(
                text="Выберите новую единицу измерения товара или добавьте новую:",
                reply_markup=kb
            )

        elif param == "count":
            await state.set_state(UpdateProduct.entering_new_count)
            await query.message.edit_text("Введите новое доступное количество товара, <b><i>например,</i></b> <code>10</code>")

        elif param == "price":
            await state.set_state(UpdateProduct.entering_new_price)
            await query.message.edit_text("Введите новую цену за одну единицу, <b><i>например,</i></b> <code>799.99</code>")

        await query.answer()

    elif query.data == "back_to_choose_product_to_update":
        await display_products_list(query, state)

    elif query.data == "confirm_param_update":
        data = await state.get_data()
        fields_to_update = {}
        for param in ("size", "count", "price", "unit_id"):
            new_key = f"new_{param}"
            if new_key in data and data[new_key] is not None:
                fields_to_update[param] = data[new_key]

        await state.clear()
        await state.update_data(catalog_id=data["catalog_id"])
        await state.update_data(category_id=data["category_id"])
        
        if fields_to_update:
            async for db in get_db():
                product = await update_object(db, Product, obj_id=data["product_id"], **fields_to_update)
            await display_products_list(query, state, start_text="✅ Товар успешно обновлён")
        else:
            await display_products_list(query, state, start_text="Нет новых изменений для сохранения")

    elif query.data == "cancel_param_update":
        data = await state.get_data()
        await state.clear()
        await state.update_data(catalog_id=data["catalog_id"])
        await state.update_data(category_id=data["category_id"])

        await display_products_list(query, state, start_text="Изменения отменены")


@admin_update_block_params.message(UpdateProduct.entering_new_size)
async def enter_new_size_for_update(mes: Message, state: FSMContext):
    try:
        new_size = float(mes.text.replace(",", "."))
        if new_size <= 0:
            raise ValueError
        
    except Exception:
        await mes.answer(text="Пожалуйства, введите неотрицательное число, <b><i>например,</i></b> <code>1.5</code>")
        return 
    
    await state.update_data(new_size=new_size)
    data = await state.get_data()
    
    async for db in get_db():
        product = await db.get(Product, data["product_id"])
        text, flag = await generate_product_info_text(db, product, data)

    kb = await generate_product_edit_keyboard(flag)

    await state.set_state(UpdateProduct.choosing_product_parametr)
    await mes.answer(
        text=text,
        reply_markup=kb
    )


@admin_update_block_params.callback_query(UpdateProduct.choosing_new_unit)
async def choose_new_unit_for_update(query: CallbackQuery, state: FSMContext):
    if query.data == "back_to_сhoose_unit_for_update":
        data = await state.get_data()
    
        async for db in get_db():
            product = await db.get(Product, data["product_id"])
            text, flag = await generate_product_info_text(db, product, data)

        kb = await generate_product_edit_keyboard(flag)

        await state.set_state(UpdateProduct.choosing_product_parametr)
        await query.message.edit_text(
            text=text,
            reply_markup=kb
        )

    elif query.data == "add_new_unit":
        await state.set_state(UpdateProduct.entering_new_unit)
        await query.message.edit_text(
            text="Введите новую единицу измерения:"
        )
        
    else:
        unit_id = int(query.data)
        data = await state.get_data()

        async for db in get_db():
            product = await db.get(Product, data["product_id"])

        if unit_id != product.unit_id:
            await state.update_data(new_unit_id=unit_id)
            data = await state.get_data()

        text, flag = await generate_product_info_text(db, product, data)

        kb = await generate_product_edit_keyboard(flag)

        await state.set_state(UpdateProduct.choosing_product_parametr)
        await query.message.edit_text(
            text=text,
            reply_markup=kb
        )


@admin_update_block_params.message(UpdateProduct.entering_new_unit)
async def enter_new_unit_for_update(mes: Message, state: FSMContext):
    unit = mes.text
    async for db in get_db():
        unit = await create_object(db, Unit, name=unit)
    
    # await state.update_data(new_unit_id=unit.id)
    async for db in get_db():
        units = await get_all(db, Unit)

    kb = await create_keyboard(units, "Добавить", "add_new_unit", "back_to_сhoose_unit_for_update")
    await state.set_state(UpdateProduct.choosing_new_unit)

    await mes.answer(
        text="Выберите новую единицу измерения:",
        reply_markup=kb
    )


@admin_update_block_params.message(UpdateProduct.entering_new_count)
async def enter_new_count_for_update(mes: Message, state: FSMContext):
    try:
        new_count = float(mes.text.replace(",", "."))
        if new_count <= 0 or new_count != int(new_count):
            raise ValueError
        
    except Exception:
        await mes.answer(text="Пожалуйства, введите целое неотрицательное число (≥ 0), <b><i>например,</i></b> <code>10</code>")
        return
    
    await state.update_data(new_count=new_count)
    data = await state.get_data()
    
    async for db in get_db():
        product = await db.get(Product, data["product_id"])
        text, flag = await generate_product_info_text(db, product, data)

    kb = await generate_product_edit_keyboard(flag)

    await state.set_state(UpdateProduct.choosing_product_parametr)
    await mes.answer(
        text=text,
        reply_markup=kb
    )


@admin_update_block_params.message(UpdateProduct.entering_new_price)
async def enter_new_proce_for_update(mes: Message, state: FSMContext):
    try:
        new_price = float(mes.text.replace(",", "."))
        if new_price <= 0:
            raise ValueError
        
    except Exception:
        await mes.answer(text="Пожалуйства, введите неотрицательное число, <b><i>например,</i></b> <code>799.99</code>")
        return
    
    await state.update_data(new_price=new_price)
    data = await state.get_data()
    
    async for db in get_db():
        product = await db.get(Product, data["product_id"])
        text, flag = await generate_product_info_text(db, product, data)

    kb = await generate_product_edit_keyboard(flag)

    await state.set_state(UpdateProduct.choosing_product_parametr)
    await mes.answer(
        text=text,
        reply_markup=kb
    )