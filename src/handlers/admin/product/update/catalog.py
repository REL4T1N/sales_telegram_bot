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

from services.product.update.catalog import display_catalog_action_menu_for_update, display_catalogs_list_for_update

admin_update_catalog = Router()

admin_update_catalog.message.filter(IsAdmin())
admin_update_catalog.callback_query.filter(IsAdmin())


@admin_update_catalog.message(Command("update_product"))
async def show_update_catalog_action(mes: Message, state: FSMContext):
    await display_catalog_action_menu_for_update(mes, state)  


@admin_update_catalog.callback_query(UpdateProduct.choosing_catalog_action)
async def choose_catalog_action(query: CallbackQuery, state: FSMContext):
    if query.data == "back_to_main_product_menu":
        #возврат в стартовое меню
        query.answer(text="СКАЗАЛ ЖЕ НЕ РАБОТАЕТ")

    if query.data == "update_catalog_name":
        await display_catalogs_list_for_update(
            query,
            state,
            new_state=UpdateProduct.choosing_catalog_rename,
            text="Выберите каталог, название которого будет изменено:"
        )

    elif query.data == "cancel_update_catalog_name":
        await display_catalogs_list_for_update(
            query,
            state,
            new_state=UpdateProduct.choosing_catalog_for_category,
            text="Выберите каталог:"
        )

    else:    
        query.answer(text="Упс... Что-то пошло не так.\nПерезапустите приложение или свяжитесь с @REL4T1NCH1k")


@admin_update_catalog.callback_query(UpdateProduct.choosing_catalog_rename)
async def choose_catalog_to_rename_for_update(query: CallbackQuery, state: FSMContext):
    if query.data == "back_update_choose_catalog_action":
        await display_catalog_action_menu_for_update(query, state)  

    else:
        catalog_id = int(query.data)
        await state.update_data(catalog_id=catalog_id)
        await state.set_state(UpdateProduct.entering_catalog_rename)

        async for db in get_db():
            catalog = await db.get(Catalog, catalog_id)

        kb = await create_back_button("back_to_choose_catalog_to_rename_for_update")
        await query.message.edit_text(
            text=f"Введите новое название для каталога <b>{catalog.name}</b>:",
            reply_markup=kb
        )

        await query.answer()


@admin_update_catalog.message(UpdateProduct.entering_catalog_rename)
async def enter_new_catalog_name_for_update(mes: Message, state: FSMContext):
    new_catalog_name = mes.text
    data = await state.get_data()
    await state.update_data(new_catalog_name=new_catalog_name)
    await state.set_state(UpdateProduct.confirming_catalog_rename)

    async for db in get_db():
        catalog = await db.get(Catalog, data["catalog_id"])

    kb = await confirming_keyboard("✅ Да", "confirm_rename_catalog_for_update", "❌ Нет", "cancel_rename_catalog_for_update")

    await mes.answer(
        text=f"Переименовать каталог <b>{catalog.name}</b> на <b>{new_catalog_name}</b>?",
        reply_markup=kb
    )


@admin_update_catalog.callback_query(UpdateProduct.entering_catalog_rename)
async def back_to_choose_catalog_to_rename_for_update(query: CallbackQuery, state: FSMContext):
    await display_catalogs_list_for_update(
        query,
        state,
        new_state=UpdateProduct.choosing_catalog_rename,
        text="Выберите каталог, название которого будет изменено:",
        clear_state=True
    )


@admin_update_catalog.callback_query(UpdateProduct.confirming_catalog_rename)
async def confirm_catalog_rename_for_update(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if query.data == "confirm_rename_catalog_for_update":
        async for db in get_db():
            catalog = await db.get(Catalog, data["catalog_id"])
            old_name = catalog.name
            new_catalog = await update_object(db, Catalog, data["catalog_id"], name=data["new_catalog_name"])

        await state.clear()
        await display_catalog_action_menu_for_update(query, state, text=f"Каталог <b>{old_name  }</b> переименован в <b>{new_catalog.name}</b>.\nВыберите действие над каталогом:")

    elif query.data == "cancel_rename_catalog_for_update":

        await state.clear()
        await display_catalog_action_menu_for_update(query, state, text="Переименование каталога отменено.\nВыберите действие над каталогом:")