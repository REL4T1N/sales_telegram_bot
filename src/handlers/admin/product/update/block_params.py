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
            text = await generate_product_info_text(db, product)

        kb = await generate_product_edit_keyboard(show_confirm_cancel=True)

        await state.set_state(UpdateProduct.choosing_product_parametr)
        await query.message.edit_text(
            text=text,
            reply_markup=kb
        )
        await query.answer()


@admin_update_block_params.callback_query(UpdateProduct.choosing_product_parametr)
async def choose_product_param_to_update(query: CallbackQuery, state: FSMContext):
    if query.data.startswith("edit_param:"):
        param = query.data.split(":")[1]
        await state.update_data(selected_param=param)

        if param == "size":
            await state.set_state(UpdateProduct.entering_new_size)
            await query.message.edit_text(text="Введите новое значение размера:")

        elif param == "unit":
            await state.set_state(UpdateProduct.choosing_new_unit)
            await query.message.edit_text("Выберите новую единицу измерения:")

        elif param == "count":
            await state.set_state(UpdateProduct.entering_new_count)
            await query.message.edit_text("Введите новое количество:")

        elif param == "price":
            await state.set_state(UpdateProduct.entering_new_price)
            await query.message.edit_text("Введите новую цену:")

        await query.answer()

    elif query.data == "back_to_choose_product_to_update":
        await display_products_list(query, state)


