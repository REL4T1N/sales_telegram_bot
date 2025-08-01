import asyncio

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.database import get_db
from database.models import Catalog, Category

from states.admin.product.update_product import UpdateProduct

from services.product.base import get_all, get_categories_by_catalog

from services.product.update.base import update_object

from handlers.admin.base import IsAdmin

from keyboards.admin.base import create_keyboard, create_back_button, confirming_keyboard
from keyboards.admin.product.update_product import catalog_action_kb


async def display_catalog_action_menu_for_update(obj, state: FSMContext, text: str = "Выберите действие над каталогом:"):
    kb = catalog_action_kb
    await state.set_state(UpdateProduct.choosing_catalog_action)

    if isinstance(obj, Message):
        await obj.answer(
            text=text,
            reply_markup=kb
        )

    elif isinstance(obj, CallbackQuery):
        await obj.message.edit_text(
            text=text,
            reply_markup=kb
        )
        await obj.answer()


async def display_catalogs_list_for_update(query: CallbackQuery, state: FSMContext, new_state: str, text: str, clear_state: bool = False):
    if clear_state:
        await state.clear()
    
    async for db in get_db():
        catalogs = await get_all(db, Catalog)
    kb = await create_keyboard(catalogs, add_back_callback="back_update_choose_catalog_action")
    
    await state.set_state(new_state)
    await query.message.edit_text(
        text=text,
        reply_markup=kb
    )
    await query.answer()