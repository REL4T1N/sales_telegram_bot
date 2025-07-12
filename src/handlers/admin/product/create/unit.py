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
    if query.data == "back_to_show_categories_list":
        await show_categories_list(query, state)

    elif query.data == "add_new_unit":

        kb = await create_back_button("back_to_units_list")

        await state.set_state(CreateProduct.entering_new_unit)
        await query.message.answer(
            text="Введите новую единицу измерения:",
            reply_markup=kb
        )
        await query.answer()

    else:
        unit_id = int(query.data)
        await state.update_data(unit_id=unit_id)
        # Нажата кнопка с id ЕИ


def register_product_create_unit(dp: Dispatcher):
    dp.callback_query.register(choose_unit, CreateProduct.choosing_unit, IsAdmin())
