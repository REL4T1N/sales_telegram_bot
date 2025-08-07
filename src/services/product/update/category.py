from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.database import get_db

from states.admin.product.update_product import UpdateProduct

from services.product.base import get_categories_by_catalog

from keyboards.admin.base import create_keyboard
from keyboards.admin.product.update_product import category_action_kb


async def display_category_action_menu_for_update(obj, state: FSMContext, text: str = "Выберите действие над категорией:"):
    kb = category_action_kb
    data = await state.get_data()
    await state.clear()

    await state.update_data(catalog_id=data["catalog_id"])
    await state.set_state(UpdateProduct.choosing_category_action)


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

async def display_category_list_for_update(query: CallbackQuery, state: FSMContext, new_state: str, text: str, clear_state: bool = False):
    data = await state.get_data()
    
    if clear_state:
        await state.clear()
        await state.update_data(catalog_id=data["catalog_id"])
    
    async for db in get_db():
        categories = await get_categories_by_catalog(db, data["catalog_id"])
    kb = await create_keyboard(categories, add_back_callback="back_update_choose_category_action")
    
    await state.set_state(new_state)
    await query.message.edit_text(
        text=text,
        reply_markup=kb
    )
    await query.answer()