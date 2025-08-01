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
from keyboards.admin.product.update_product import category_action_kb

from services.product.update.catalog import display_catalog_action_menu_for_update, display_catalogs_list_for_update
from services.product.update.category import display_category_action_menu_for_update, display_category_list_for_update

admin_update_category = Router()

admin_update_category.message.filter(IsAdmin())
admin_update_category.callback_query.filter(IsAdmin())


@admin_update_category.callback_query(UpdateProduct.choosing_catalog_for_category)
async def choose_catalog_to_step_category_for_update(query: CallbackQuery, state: FSMContext):
    if query.data == "back_update_choose_catalog_action":
        await display_catalog_action_menu_for_update(query, state)

    else:
        catalog_id = int(query.data)
        await state.update_data(catalog_id=catalog_id)
        
        await display_category_action_menu_for_update(query, state)


@admin_update_category.callback_query(UpdateProduct.choosing_category_action)
async def choose_category_action_for_update(query: CallbackQuery, state: FSMContext):
    if query.data == "back_to_choose_catalog_for_category":
        await display_catalogs_list_for_update(
            query,
            state,
            new_state=UpdateProduct.choosing_catalog_for_category,
            text="Выберите каталог:",
            clear_state=True
        )

    elif query.data == "update_category_name":
        await display_category_list_for_update(
            query,
            state,
            new_state=UpdateProduct.choosing_category_rename,
            text="Выберите категорию, название которой будет изменено:",
        )

    elif query.data == "cancel_update_category_name":
        await display_category_list_for_update(
            query,
            state,
            new_state=UpdateProduct.choosing_category_for_size,
            text="Выберите категорию:",
        )

    else:    
        query.answer(text="Упс... Что-то пошло не так.\nПерезапустите приложение или свяжитесь с @REL4T1NCH1k")


@admin_update_category.callback_query(UpdateProduct.choosing_category_rename)
async def choose_category_to_rename_for_update(query: CallbackQuery, state: FSMContext):
    if query.data == "back_update_choose_category_action":
        await display_category_action_menu_for_update(query, state)

    else:
        category_id = int(query.data)

        await state.update_data(category_id=category_id)
        kb = await create_back_button("back_to_choose_category_to_rename_for_update")

        async for db in get_db():
            category = await db.get(Category, category_id)

        await state.set_state(UpdateProduct.entering_category_rename)
        await query.message.edit_text(
            text=f"Введите новое название для категории <b>{category.name}</b>:",
            reply_markup=kb
        )


@admin_update_category.message(UpdateProduct.entering_category_rename)
async def enter_new_category_name_for_update(mes: Message, state: FSMContext):
    new_category_name = mes.text
    data = await state.get_data()

    async for db in get_db():
        category = await db.get(Category, data["category_id"])

    kb = await confirming_keyboard("✅ Да", "confirm_rename_category_for_update", "❌ Нет", "cancel_rename_category_for_update")

    await state.update_data(new_category_name=new_category_name)
    await state.set_state(UpdateProduct.confirming_category_rename)

    await mes.answer(
        text=f"Переименовать категорию <b>{category.name}</b> на <b>{new_category_name}</b>?",
        reply_markup=kb
    )


@admin_update_category.callback_query(UpdateProduct.entering_category_rename)
async def back_to_category_to_rename_for_update(query: CallbackQuery, state: FSMContext):
    await display_category_list_for_update(
        query,
        state,
        new_state=UpdateProduct.choosing_category_rename,
        text="Выберите категорию, название которой будет изменено:",
        clear_state=True
    )


@admin_update_category.callback_query(UpdateProduct.confirming_category_rename)
async def confirm_category_rename_for_update(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if query.data == "confirm_rename_category_for_update":
        async for db in get_db():
            category = await db.get(Category, data["category_id"])
            old_name = category.name
            new_category = await update_object(db, Category, data["category_id"], catalog_id=data["catalog_id"], name=data["new_category_name"])

        await display_category_action_menu_for_update(query, state, text=f"Категория <b>{old_name}</b> переименована в <b>{new_category.name}</b>.\nВыберите действие над категорией:")

    elif query.data == "cancel_rename_category_for_update":

        await display_category_action_menu_for_update(query, state, text="Переименование категории отменено.\nВыберите действие над категорией:")    