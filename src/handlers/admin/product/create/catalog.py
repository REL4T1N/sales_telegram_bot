from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.database import get_db
from database.models import Catalog

from states.admin.product.create_product import CreateProduct

from services.product.base import get_all, create_object

from services.product.create import get_categories_by_catalog

from handlers.admin.base import IsAdmin

from keyboards.admin.base import create_keyboard, create_back_button, confirming_keyboard

admin_create_catalog = Router()

admin_create_catalog.message.filter(IsAdmin())
admin_create_catalog.callback_query.filter(IsAdmin())

'''
В данный момент нет продуманного меню, отображающего выбор действий, типо добавлять, 
редактировать и тд, поэтому будет команда для создания "/create_product"
'''
@admin_create_catalog.message(Command("create_product"))
async def show_catalogs_list(mes: Message, state: FSMContext):
    async for db in get_db():
        catalogs = await get_all(db, Catalog)

    kb = await create_keyboard(catalogs, "Добавить", "add_new_catalog", "back_to_main_product_menu")
    
    await state.set_state(CreateProduct.choosing_catalog)
    await mes.answer(
        text="Выберите каталог или добавьте новый:",
        reply_markup=kb
    )


@admin_create_catalog.callback_query(CreateProduct.choosing_catalog)
async def choose_catalog_to_create(query: CallbackQuery, state: FSMContext):
    if query.data == "back_to_main_product_menu":
        # была нажата кнопка назад для отображения основного меню работы админа над продуктами
        pass

    elif query.data == "add_new_catalog":
        # была нажата кнопка добавить новый каталог
        kb = await create_back_button("back_to_show_catalogs_list")

        await state.set_state(CreateProduct.entering_catalog_name)
        await query.message.edit_text(
            text="Введите название нового каталога:",
            reply_markup=kb
        )
        await query.answer()

    else:
        # была нажата кнопка одного из видов каталогов, т.е. кнопка с id доступного каталога
        catalog_id = int(query.data)
        await state.update_data(catalog_id=catalog_id)
        await show_categories_list(query, state)
        return


@admin_create_catalog.message(CreateProduct.entering_catalog_name)
async def enter_new_catalog_name(mes: Message, state: FSMContext):
    catalog_name = mes.text
    await state.update_data(catalog_name=catalog_name)

    '''лучше добавить подтверждение'''
    kb = await confirming_keyboard("✅ Да", "confirm_add_catalog", "❌ Нет", "cancel_add_catalog")

    await state.set_state(CreateProduct.confirming_catalog_name)
    await mes.answer(
        text=f"Добавить каталог <b>{catalog_name}</b>?",
        reply_markup=kb
    )


@admin_create_catalog.callback_query(CreateProduct.entering_catalog_name)
async def back_to_show_catalogs_list(query: CallbackQuery, state: FSMContext):
    async for db in get_db():
        catalogs = await get_all(db, Catalog)

    kb = await create_keyboard(catalogs, "Добавить", "add_new_catalog", "back_to_main_product_menu")
    
    await state.set_state(CreateProduct.choosing_catalog)
    await query.message.edit_text(
        text="Выберите каталог или добавьте новый:",
        reply_markup=kb
    )
    await query.answer()


@admin_create_catalog.callback_query(CreateProduct.confirming_catalog_name)
async def confirm_catalog_name(query: CallbackQuery, state: FSMContext):
    if query.data == "confirm_add_catalog":

        data = await state.get_data()
        async for db in get_db():
            catalog = await create_object(db, Catalog, name=data["catalog_name"])
        
        await query.answer(text="✅ Каталог успешно добавлен")
        await state.clear()
        await back_to_show_catalogs_list(query, state)
        return

    elif query.data == "cancel_add_catalog":
        await query.answer(text="❌ Добавление каталога отменено")
        await state.clear()
        await back_to_show_catalogs_list(query, state)
        return
        
    else:
        query.answer(text="Упс... Что-то пошло не так.\nПерезапустите приложение или свяжитесь с @REL4T1NCH1k")


@admin_create_catalog.callback_query(CreateProduct.choosing_catalog)
async def show_categories_list(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    async for db in get_db():
        categories = await get_categories_by_catalog(db, data["catalog_id"])

    kb = await create_keyboard(categories, "Добавить", "add_new_category", "back_to_show_catalogs_list")

    await state.set_state(CreateProduct.choosing_category)
    await query.message.edit_text(
        text="Выберите категорию или добавьте новую:",
        reply_markup=kb
    )
    await query.answer()