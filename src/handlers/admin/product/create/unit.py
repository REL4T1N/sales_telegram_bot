from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.database import get_db
from database.models import Catalog, Category, Unit, Product

from states.admin.product.create_product import CreateProduct

from services.product.base import get_all, create_object

from services.product.create import get_categories_by_catalog

from utils.formatting_float_nums import pretty_num

from schemas.product import ProductCreate

from handlers.admin.base import IsAdmin

from keyboards.admin.base import create_keyboard, create_back_button, confirming_keyboard

from handlers.admin.product.create.catalog import show_categories_list, back_to_show_catalogs_list
from handlers.admin.product.create.category import show_units_list, show_categories_list


async def choose_unit(query: CallbackQuery, state: FSMContext):
    if query.data == "back_to_enter_size":
        data = await state.get_data()

        kb = await create_back_button("back_to_categories_list")

        await state.clear()
        await state.update_data(catalog_id=data["catalog_id"])
        await state.update_data(category_id=data["category_id"])
        
        await state.set_state(CreateProduct.entering_size)
        await query.message.edit_text(
            text="Введите размер одной единицы товара, <b><i>например,</i></b> <code>1.5</code>",
            reply_markup=kb
        )
        await query.answer()
        return 

    kb = await create_back_button("back_to_units_list")

    if query.data == "add_new_unit":
        await state.set_state(CreateProduct.entering_new_unit)
        await query.message.edit_text(
            text="Введите новую единицу измерения:",
            reply_markup=kb
        )
        await query.answer()

    else:
        unit_id = int(query.data)
        await state.update_data(unit_id=unit_id)
        await state.set_state(CreateProduct.entering_count)
        await query.message.edit_text(
            text="Введите доступное количество товара, <b><i>например,</i></b> <code>10</code>",
            reply_markup=kb
        )
        await query.answer()
        # Нажата кнопка с id ЕИ
        

async def back_to_units_list(query: CallbackQuery, state: FSMContext):
    if query.data == "back_to_units_list":

        data = await state.get_data()
        await state.clear()
        await state.update_data(catalog_id=data["catalog_id"])
        await state.update_data(category_id=data["category_id"])
        await state.update_data(size=data["size"])
        await show_units_list(query, state)
        return

    else:
        query.answer(text="Упс... Что-то пошло не так.\nПерезапустите приложение или свяжитесь с @REL4T1NCH1k")


async def enter_new_unit(mes: Message, state: FSMContext):
    unit = mes.text
    await state.update_data(unit=unit)
    
    kb = await confirming_keyboard("✅ Да", "confirm_add_unit", "❌ Нет", "cancel_add_unit")

    await state.set_state(CreateProduct.confirming_new_unit)
    await mes.answer(
        text=f"Добавить единицу измерения <b>{unit}</b>?",
        reply_markup=kb
    )


async def confirm_unit(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if query.data == "confirm_add_unit":
        async for db in get_db():
            unit = await create_object(db, Unit, name=data["unit"])

        await query.answer(text="✅ Категория успешно добавлена")
        await state.clear()
        await state.update_data(catalog_id=data["catalog_id"])
        await state.update_data(category_id=data["category_id"])
        await state.update_data(size=data["size"])
        await show_units_list(query, state)
        return

    elif query.data == "cancel_add_unit":
        await query.answer(text="❌ Добавление категории отменено")
        await state.clear()
        await state.update_data(catalog_id=data["catalog_id"])
        await state.update_data(category_id=data["category_id"])
        await state.update_data(size=data["size"])
        await show_units_list(query, state)
        return

    else:
        query.answer(text="Упс... Что-то пошло не так.\nПерезапустите приложение или свяжитесь с @REL4T1NCH1k")


def register_product_create_unit(dp: Dispatcher):
    dp.callback_query.register(choose_unit, CreateProduct.choosing_unit, IsAdmin())
    dp.callback_query.register(back_to_units_list, CreateProduct.entering_new_unit, IsAdmin())
    dp.message.register(enter_new_unit, CreateProduct.entering_new_unit, IsAdmin())
    dp.callback_query.register(confirm_unit, CreateProduct.confirming_new_unit, IsAdmin())