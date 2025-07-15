from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.database import get_db
from database.models import Catalog, Category, Unit

from states.admin.product.create_product import CreateProduct

from services.product.base import get_all, create_object

from handlers.admin.base import IsAdmin

from keyboards.admin.base import create_keyboard, create_back_button, confirming_keyboard

from handlers.admin.product.create.catalog import show_categories_list, back_to_show_catalogs_list


admin_create_category = Router()
admin_create_category.message.filter(IsAdmin())
admin_create_category.callback_query.filter(IsAdmin())


@admin_create_category.callback_query(CreateProduct.choosing_category)
async def choose_category(query: CallbackQuery, state: FSMContext):
    if query.data == "back_to_show_catalogs_list":
        await back_to_show_catalogs_list(query, state)
        return

    kb = await create_back_button("back_to_categories_list")

    if query.data == "add_new_category":
        data = await state.get_data()
        async for db in get_db():
            catalog = await db.get(Catalog, data["catalog_id"])

        await state.set_state(CreateProduct.entering_category_name)
        await query.message.edit_text(
            text=f"Введите название новой категории для каталога <b>{catalog.name}</b>:",
            reply_markup=kb
        )
        await query.answer()
    
    else:
        category_id = int(query.data)
        await state.update_data(category_id=category_id)
        await state.set_state(CreateProduct.entering_size)
        await query.message.edit_text(
            text="Введите размер одной единицы товара, <b><i>например,</i></b> <code>1.5</code>",
            reply_markup=kb
        )
        await query.answer()


@admin_create_category.callback_query(CreateProduct.entering_category_name)
async def back_to_categories_list(query: CallbackQuery, state: FSMContext):
    if query.data == "back_to_categories_list":

        data = await state.get_data()
        await state.clear()
        await state.update_data(catalog_id=data["catalog_id"])
        await show_categories_list(query, state)
        return

    else:
        query.answer(text="Упс... Что-то пошло не так.\nПерезапустите приложение или свяжитесь с @REL4T1NCH1k")


@admin_create_category.message(CreateProduct.entering_category_name)
async def enter_new_category_name(mes: Message, state: FSMContext):
    category_name = mes.text
    data = await state.get_data()
    await state.update_data(category_name=category_name)
    
    async for db in get_db():
        catalog = await db.get(Catalog, data["catalog_id"])

    kb = await confirming_keyboard("✅ Да", "confirm_add_category", "❌ Нет", "cancel_add_category")

    await state.set_state(CreateProduct.confirming_category_name)
    await mes.answer(
        text=f"Добавить категорию <b>{category_name}</b> для каталога <b>{catalog.name}</b>?",
        reply_markup=kb
    )


@admin_create_category.callback_query(CreateProduct.confirming_category_name)
async def confirm_category_name(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if query.data == "confirm_add_category":
        async for db in get_db():
            category = await create_object(db, Category, catalog_id=data["catalog_id"], name=data["category_name"])

        await query.answer(text="✅ Категория успешно добавлена")
        await state.clear()
        await state.update_data(catalog_id=data["catalog_id"])
        await show_categories_list(query, state)
        return

    elif query.data == "cancel_add_category":
        await query.answer(text="❌ Добавление категории отменено")
        await state.clear()
        await state.update_data(catalog_id=data["catalog_id"])
        await show_categories_list(query, state)
        return

    else:
        query.answer(text="Упс... Что-то пошло не так.\nПерезапустите приложение или свяжитесь с @REL4T1NCH1k")

@admin_create_category.callback_query(CreateProduct.entering_size)
async def show_units_list(query: CallbackQuery, state: FSMContext):
    async for db in get_db():
        units = await get_all(db, Unit)

    kb = await create_keyboard(units, "Добавить", "add_new_unit", "back_to_show_categories_list")

    await state.set_state(CreateProduct.choosing_unit)
    await query.message.edit_text(
        text="Выберите единицу измерения товара или добавьте новую:",
        reply_markup=kb
    )
    await query.answer()