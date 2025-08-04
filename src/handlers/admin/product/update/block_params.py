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

from services.product.base import get_all, get_categories_by_catalog

from services.product.update.base import update_object

from handlers.admin.base import IsAdmin

from keyboards.admin.base import create_keyboard, create_back_button, confirming_keyboard
from keyboards.admin.product.update_product import catalog_action_kb

from services.product.update.catalog import display_catalog_action_menu_for_update, display_catalogs_list_for_update
from services.product.update.category import display_category_action_menu_for_update, display_category_list_for_update
from services.product.update.block_params import generate_products_table


from utils.formatting_float_nums import pad, pretty_num, pretty_edit

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
        data = await state.get_data()

        async for db in get_db():
            products = await db.execute(
                select(Product).where(Product.category_id == category_id)
            )
            products = products.scalars().all()

            catalog = await db.get(Catalog, data["catalog_id"])
            category = await db.get(Category, data["category_id"])
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
                buttons_per_row=3
            )

            await state.set_state(UpdateProduct.choose_product_parametr_to_edit)
            await query.message.edit_text(
                text=text,
                reply_markup=kb,
                parse_mode="MarkdownV2"
            )
            await query.answer()