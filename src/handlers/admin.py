from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart, CommandObject, BaseFilter
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.fsm.context import FSMContext

from keyboards.start_keyboard import start_admin_keyboard
from keyboards.admin_update_catalog import work_with_catalog_keyboard, back_to_catalog_keyboard, yes_or_cancel_keyboard

from database.database import get_db
from services.product.common import get_all, create_object
from services.product.product import get_categories_by_catalog, get_product_display_data
from database.models import Catalog, Category, Unit, Product
from keyboards.common import create_keyboard
from utils.formatting_float_nums import pretty_num

from schemas.catalog import ProductCreate

from states.product import AddProductStates

admin_ids = [6376753355]

class IsAdmin(BaseFilter):
    async def __call__(self, obj: TelegramObject) -> bool:
        return obj.from_user.id in admin_ids
    

async def start_command(mes: Message):
    await mes.answer(
        text="Выберите",
        reply_markup=start_admin_keyboard                 
    )


async def work_with_products(mes: Message):
    await mes.answer(
        text="Выберите действие",
        reply_markup=work_with_catalog_keyboard
    )

# 1. Запуск добавления товара
async def add_product_start(query: CallbackQuery, state: FSMContext):
    async for db in get_db():
        catalogs = await get_all(db, Catalog)
    
    kb = create_keyboard(catalogs, "Добавить новый каталог", "add_new_catalog")

    await state.set_state(AddProductStates.choosing_catalog)
    await query.message.answer(text="Выберите каталог или добавьте новый:", reply_markup=kb)
    await query.answer()

# 2. Выбор каталога или добавление нового
async def choose_catalog(query: CallbackQuery, state: FSMContext):
    data = query.data
    if data == "add_new_catalog":
        await state.set_state(AddProductStates.entering_catalog)
        await query.message.answer(text="Введите название нового каталога")
        await query.answer()

    else:
        catalog_id = int(data)
        await state.update_data(catalog_id=catalog_id)
        async for db in get_db():
            categories = await get_categories_by_catalog(db, catalog_id)
        
        kb = create_keyboard(categories, "Добавить новую категорию", "add_new_category")

        await state.set_state(AddProductStates.choosing_category)
        await query.message.answer(text="Выберите категорию или добавьте новую:", reply_markup=kb)
        await query.answer()

# 3. Ввод нового каталога
async def enter_new_catalog(mes: Message, state: FSMContext):
    async for db in get_db():
        catalog = await create_object(db, Catalog, name=mes.text)

    await state.update_data(catalog_id=catalog.id)

    async for db in get_db():
        categories = await get_categories_by_catalog(db, catalog.id)
    
    kb = create_keyboard(categories, "Добавить новую категорию", "add_new_category")

    await state.set_state(AddProductStates.choosing_category)
    await mes.answer(text="Выберите категорию или добавьте новую:", reply_markup=kb)

# 4. Выбор или добавление категории
async def choose_category(query: CallbackQuery, state: FSMContext):
    data = query.data

    if data == "add_new_category":
        await state.set_state(AddProductStates.entering_category)
        await query.message.answer(text="Введите название новой категории")
        await query.answer()

    else:
        category_id = int(data)
        await state.update_data(category_id=category_id)
        
        async for db in get_db():
            units = await get_all(db, Unit)

        kb = create_keyboard(units, "Добавить новую единицу", "add_new_unit")
        
        await state.set_state(AddProductStates.choosing_unit)
        await query.message.answer(text="Выберите единицу измерения или добавьте новую:", reply_markup=kb)
        await query.answer()
        
# 5. Ввод новой категории
async def enter_new_category(mes: Message, state: FSMContext):
    data = await state.get_data()

    async for db in get_db():
        category = await create_object(db, Category, catalog_id=data["catalog_id"], name=mes.text)

    await state.update_data(category_id=category.id)
    async for db in get_db():
        units = await get_all(db, Unit)

    kb = create_keyboard(units, "Добавить новую единицу", "add_new_unit")
    
    await state.set_state(AddProductStates.choosing_unit)
    await mes.answer(text="Выберите единицу измерения или добавьте новую:", reply_markup=kb)

        
# 6. Выбор или добавлении единицы измерения
async def choose_unit(query: CallbackQuery, state: FSMContext):
    data = query.data
    if data == "add_new_unit":
        await state.set_state(AddProductStates.entering_unit)
        await query.message.answer(text="Введите новую единицу измерения:")
        await query.answer()

    else:
        unit_id = int(data)
        await state.update_data(unit_id=unit_id)
        await state.set_state(AddProductStates.entering_size)
        await query.message.answer(text="Введите размер одной единицы товара, <b><i>например,</i></b> <code>1.5</code>")
        await query.answer()

# 7. Ввод новой единицы измерения
async def enter_new_unit(mes: Message, state: FSMContext):
    async for db in get_db():
        unit = await create_object(db, Unit, name=mes.text)
    
    await state.update_data(unit_id=unit.id)
    await state.set_state(AddProductStates.entering_size)
    await mes.answer(text="Введите размер одной единицы товара, <b><i>например,</i></b> <code>1.5</code>")

# 8. Ввод размера одной единицы
async def enter_size(mes: Message, state: FSMContext):
    try:
        size = float(mes.text.replace(",", "."))
        if size <= 0:
            raise ValueError
        
    except Exception:
        await mes.answer(text="Пожалуйства, введите неотрицательное число, <b><i>например,</i></b> <code>1.5</code>")
        return 
    
    await state.update_data(size=size)
    await state.set_state(AddProductStates.entering_quantity)
    await mes.answer(text="Введите количество, <b><i>например,</i></b> <code>10</code>")

# 9. Ввод количества
async def enter_count(mes: Message, state: FSMContext):
    try:
        count = float(mes.text.replace(",", "."))
        if count <= 0 or count != int(count):
            raise ValueError
        
    except Exception:
        await mes.answer(text="Пожалуйства, введите целое неотрицательное число, <b><i>например,</i></b> <code>10</code>")
        return 
    
    await state.update_data(quantity=count)
    await state.set_state(AddProductStates.entering_price)
    await mes.answer(text="Введите цену за одну единицу, <b><i>например,</i></b> <code>799.99</code>")

# 10. Ввод цены
async def enter_price(mes: Message, state: FSMContext):
    try:
        price = float(mes.text.replace(",", "."))
        if price <= 0:
            raise ValueError
        
    except Exception:
        await mes.answer(text="Пожалуйства, введите неотрицательное число, <b><i>например,</i></b> <code>799.99</code>")
        return 
    
    await state.update_data(price=price)
    data = await state.get_data()

    async for db in get_db():
        names = await get_product_display_data(
            db, 
            data["catalog_id"],
            data["category_id"],
            data["unit_id"]
        )

    text = (
        f"Товар успешно добавлен!\n\n"
        f"Каталог: {names['catalog_name']}\n"
        f"Категория: {names['category_name']}\n"
        f"Размер одной: {pretty_num(data['size'])} {names['unit_name']}\n"
        f"Количество: {pretty_num(data['quantity'])}\n"
        f"Цена: {pretty_num(data['price'])}\n"
    )

    kb = yes_or_cancel_keyboard

    await state.set_state(AddProductStates.confirming)
    await mes.answer(text, reply_markup=kb)  

# 11. Подтверждение и создание товара
async def confirm_product(query: CallbackQuery, state: FSMContext):
    data = query.data

    if data == "yes_create_product":
        data = await state.get_data()
        product_create = ProductCreate(
            category_id=data["category_id"],
            unit_id=data["unit_id"],
            available=True,
            size=data["size"],
            quantity=data["quantity"],
            price=data["price"]
        )

        async for db in get_db():
            product = await create_object(db, Product, **product_create.dict())
            names = await  get_product_display_data(
                db, 
                data["catalog_id"],
                data["category_id"],
                data["unit_id"]
            )

        text = (
            f"Каталог: {names['catalog_name']}\n"
            f"Категория: {names['category_name']}\n"
            f"Размер одной: {pretty_num(data['size'])} {names['unit_name']}\n"
            f"Количество: {pretty_num(data['quantity'])}\n"
            f"Цена: {pretty_num(data['price'])}\n"
            "Добавить этот товар?"
        )

        await query.message.answer(text=text)
        await query.answer(text="Добавлено ✅", show_alert=False)
        await state.clear()
    
    elif query.data == "cancel_create_product":
        kb = work_with_catalog_keyboard

        await query.message.answer(
            text="Добавление товара отменено.",
            reply_markup=kb
        )
        await query.answer(text="Отлично", show_alert=False)
        await state.clear()

    else:
        await query.answer()
        
# 12. Регистрация хендлеров
def admin_handlers(dp: Dispatcher):
    dp.message.register(start_command, CommandStart(), IsAdmin())
    dp.message.register(work_with_products, F.text == "Обновить каталог", IsAdmin())
    dp.callback_query.register(add_product_start, F.data == "create_category", IsAdmin())
    dp.callback_query.register(choose_catalog, AddProductStates.choosing_catalog, IsAdmin())
    dp.message.register(enter_new_catalog, AddProductStates.entering_catalog, IsAdmin())
    dp.callback_query.register(choose_category, AddProductStates.choosing_category, IsAdmin())
    dp.message.register(enter_new_category, AddProductStates.entering_category, IsAdmin())
    dp.callback_query.register(choose_unit, AddProductStates.choosing_unit, IsAdmin())
    dp.message.register(enter_new_unit, AddProductStates.entering_unit, IsAdmin())
    dp.message.register(enter_size, AddProductStates.entering_size, IsAdmin())
    dp.message.register(enter_count, AddProductStates.entering_quantity, IsAdmin())
    dp.message.register(enter_price, AddProductStates.entering_price, IsAdmin())
    dp.callback_query.register(confirm_product, AddProductStates.confirming, IsAdmin())
