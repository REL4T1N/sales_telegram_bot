from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.database import get_db
from database.models import Product, Unit

from states.admin.product.update_product import UpdateProduct

from services.product.base import get_all
from services.product.create import create_object
from services.product.update.category import display_category_action_menu_for_update, display_category_list_for_update
from services.product.update.block_params import display_products_list, handle_param_input, confirm_changes, cancel_changes

from handlers.admin.base import IsAdmin

from keyboards.admin.base import create_keyboard
from keyboards.admin.product.update_product import generate_product_edit_keyboard

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
            query, state, UpdateProduct.choosing_category_for_blocks,
            text="Выберите категорию:", clear_state=True
        )
    else:
        product_id = int(query.data)
        await state.update_data(product_id=product_id)
        async for db in get_db():
            product = await db.get(Product, product_id)
            text, flag = await generate_product_info_text(db, product)
        kb = await generate_product_edit_keyboard(flag)
        await state.set_state(UpdateProduct.choosing_product_parametr)
        await query.message.edit_text(text=text, reply_markup=kb)
        await query.answer()


@admin_update_block_params.callback_query(UpdateProduct.choosing_product_parametr)
async def choose_product_param_to_update(query: CallbackQuery, state: FSMContext):
    param_actions = {
        "size": {"state": UpdateProduct.entering_new_size, "text": "Введите новый размер одной единицы товара, <b><i>например,</i></b> <code>1.5</code>"},
        "unit": {"state": UpdateProduct.choosing_new_unit, "text": "Выберите новую единицу измерения товара или добавьте новую:"},
        "count": {"state": UpdateProduct.entering_new_count, "text": "Введите новое доступное количество товара, <b><i>например,</i></b> <code>10</code>"},
        "price": {"state": UpdateProduct.entering_new_price, "text": "Введите новую цену за одну единицу, <b><i>например,</i></b> <code>799.99</code>"}
    }

    if query.data.startswith("update_param:"):
        param = query.data.split(":")[1]
        if param in param_actions:
            await state.set_state(param_actions[param]["state"])
            if param == "unit":
                async for db in get_db():
                    units = await get_all(db, Unit)
                kb = await create_keyboard(units, "Добавить", "add_new_unit", "back_to_сhoose_unit_for_update")
                await query.message.edit_text(text=param_actions[param]["text"], reply_markup=kb)
            else:
                await query.message.edit_text(text=param_actions[param]["text"])
            await query.answer()
    elif query.data == "back_to_choose_product_to_update":
        await display_products_list(query, state)
    elif query.data == "confirm_param_update":
        await confirm_changes(query, state)
    elif query.data == "cancel_param_update":
        await cancel_changes(query, state)


@admin_update_block_params.message(UpdateProduct.entering_new_size)
async def enter_new_size_for_update(mes: Message, state: FSMContext):
    await handle_param_input("size", mes, state)


@admin_update_block_params.callback_query(UpdateProduct.choosing_new_unit)
async def choose_new_unit_for_update(query: CallbackQuery, state: FSMContext):
    if query.data == "back_to_сhoose_unit_for_update":
        data = await state.get_data()
        async for db in get_db():
            product = await db.get(Product, data["product_id"])
            text, flag = await generate_product_info_text(db, product, data)
        kb = await generate_product_edit_keyboard(flag)
        await state.set_state(UpdateProduct.choosing_product_parametr)
        await query.message.edit_text(text=text, reply_markup=kb)
    elif query.data == "add_new_unit":
        await state.set_state(UpdateProduct.entering_new_unit)
        await query.message.edit_text(text="Введите новую единицу измерения:")
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
        await query.message.edit_text(text=text, reply_markup=kb)


@admin_update_block_params.message(UpdateProduct.entering_new_unit)
async def enter_new_unit_for_update(mes: Message, state: FSMContext):
    unit_name = mes.text
    async for db in get_db():
        unit = await create_object(db, Unit, name=unit_name)
        units = await get_all(db, Unit)
    kb = await create_keyboard(units, "Добавить", "add_new_unit", "back_to_сhoose_unit_for_update")
    await state.set_state(UpdateProduct.choosing_new_unit)
    await mes.answer(text="Выберите новую единицу измерения:", reply_markup=kb)


@admin_update_block_params.message(UpdateProduct.entering_new_count)
async def enter_new_count_for_update(mes: Message, state: FSMContext):
    await handle_param_input("count", mes, state)


@admin_update_block_params.message(UpdateProduct.entering_new_price)
async def enter_new_price_for_update(mes: Message, state: FSMContext):
    await handle_param_input("price", mes, state)