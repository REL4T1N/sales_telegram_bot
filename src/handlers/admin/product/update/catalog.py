from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.database import get_db
from database.models import Catalog, Category

from states.admin.product.update_product import UpdateProduct

from services.product.base import get_all, get_categories_by_catalog

from services.product.update import update_object

from handlers.admin.base import IsAdmin

from keyboards.admin.base import create_keyboard, create_back_button, confirming_keyboard
from keyboards.admin.product.update_product import catalog_action_kb


admin_update_catalog = Router()

admin_update_catalog.message.filter(IsAdmin())
admin_update_catalog.callback_query.filter(IsAdmin())


@admin_update_catalog.message(Command("update_product"))
async def show_update_catalog_action(mes: Message, state: FSMContext):
    kb = catalog_action_kb

    await state.set_state(UpdateProduct.choosing_catalog_action)
    await mes.answer(
        text="Выберите действие над каталогом:",
        reply_markup=kb
    )


@admin_update_catalog.callback_query(UpdateProduct.choosing_catalog_action)
async def choose_catalog_action(query: CallbackQuery, state: FSMContext):
    if query.data == "back_to_main_product_menu":
        #возврат в стартовое меню
        query.answer(text="СКАЗАЛ ЖЕ НЕ РАБОТАЕТ")

    elif query.data == "update_catalog_name":
        # обновление каталога
        pass

    elif query.data == "cancel_update_catalog_name":
        async for db in get_db():
            catalogs = await get_all(db, Catalog)

        kb = await create_keyboard(catalogs, add_back_callback="back_update_choose_catalog_action")
        await state.set_state(UpdateProduct.choosing_catalog_for_category) 
        await query.message.answer(
            text="Выберите каталог или добавьте новый:",
            reply_markup=kb
        )
        await query.answer()

    else:    
        query.answer(text="Упс... Что-то пошло не так.\nПерезапустите приложение или свяжитесь с @REL4T1NCH1k")
