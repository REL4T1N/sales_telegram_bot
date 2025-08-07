from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.database import get_db
from database.models import Unit

from states.admin.product.create_product import CreateProduct

from services.product.create import create_object

from handlers.admin.base import IsAdmin
from handlers.admin.product.create.category import show_units_list

from keyboards.admin.base import create_back_button, confirming_keyboard


admin_create_unit = Router()
admin_create_unit.message.filter(IsAdmin())
admin_create_unit.callback_query.filter(IsAdmin())


@admin_create_unit.callback_query(CreateProduct.choosing_unit)
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
        

@admin_create_unit.callback_query(CreateProduct.entering_new_unit)
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


@admin_create_unit.message(CreateProduct.entering_new_unit)
async def enter_new_unit(mes: Message, state: FSMContext):
    unit = mes.text
    await state.update_data(unit=unit)
    
    kb = await confirming_keyboard("✅ Да", "confirm_add_unit", "❌ Нет", "cancel_add_unit")

    await state.set_state(CreateProduct.confirming_new_unit)
    await mes.answer(
        text=f"Добавить единицу измерения <b>{unit}</b>?",
        reply_markup=kb
    )


@admin_create_unit.callback_query(CreateProduct.confirming_new_unit)
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