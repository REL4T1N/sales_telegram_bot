import asyncio

from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from handlers.admin import IsAdmin, admin_ids

from database.database import get_db
from database.models import Catalog, Category, Product, Unit

from utils.formatting_float_nums import pretty_num

from states.product import UpdateProductStates

from services.product.common import create_object, update_object, get_all
from services.product.product import get_categories_by_catalog

from keyboards.common import create_keyboard
from keyboards.admin_update_catalog import work_with_catalog_keyboard

# нужен форматер данных после выбора категории

'''
ДЕЙСТВУЮ НЕПРАВИЛЬНО
Я СРАЗУ НАЧИНАЮ С ВЫБОРА, ХОТЯ СНАЧАЛА СТОИТ ПРОСТО ОТОБРАЗИТЬ ПЕРВОЕ ОКНО
ЗАДАЧИ:
    1)ДОБАВИТЬ НУЛЕВОЙ ШАГ, 
    2)ПРОВЕСТИ РЕНЕЙМ ФУНКИЙ, 
    3)ИЗМЕНИТЬ ШАГИ

'''











# 1. Выбор: Выбрать каталог или изменить навазние каталога
# 1.1 Выбрать каталог: Отображаем все каталоги и кнопку назад -> Выбор дейстивем над категориями
# 1.2 Изменить название каталога: Отоюражаем все названия каталогов для изменения и кнопку назад
# 1.3 Если решили менять название каталога и выбрали соответствующий каталог, то вводим его название
# 1.4 После ввода нового значения названия каталога просим подтвердить его -> Меню выбора названия каталога
# 
# 2. 
#
#
#
#

# Реализуем Пункты 1*

# Выбор действия над каталогом
async def choose_catalog_to_step_or_to_rename(query: CallbackQuery, state: FSMContext):
    buttons = [
        [
            InlineKeyboardButton(text="Не менять имени каталога", callback_data="show_catalogs_list"),
            InlineKeyboardButton(text="Изменить имя каталога", callback_data="show_catalogs_list_to_rename")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await state.set_state(UpdateProductStates.choose_catalog_action)
    await query.message.answer(text="Выберите действие:", reply_markup=kb)
    await query.answer()

# Распределение действий над каталогом, выборы двух случаев
async def show_catalogs_for_choose_action(query: CallbackQuery, state: FSMContext):
    data = query.data

    if data == "back_to_main_menu":
        await state.set_state(UpdateProductStates.back_to_main_menu)
        await back_to_main_menu(query, state)
        return 
        # await state.clear()  
        # await query.message.answer(
        #     text="Выберите действие:",
        #     reply_markup=work_with_catalog_keyboard
        # )
        # await query.answer()
        # return
    
    async for db in get_db():
        catalogs = await get_all(db, Catalog)
        kb = create_keyboard(catalogs, "Назад", "back_to_choose_catalog_action")

    if data == "show_catalogs_list":
        await state.set_state(UpdateProductStates.choose_catalog)
        await query.message.answer(
            text="Выберите каталог:",
            reply_markup=kb
        )
        await query.answer()

    elif data == "show_catalogs_list_to_rename":
        await state.set_state(UpdateProductStates.choose_catalog_to_rename)
        await query.message.answer(
            text="Выберите каталог, название которого будет изменено:",
            reply_markup=kb
        )
        await query.answer()

    else:
        await query.answer(text="Сосал?")


async def back_to_main_menu(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.answer(
        text="Выберите действие",
        reply_markup=work_with_catalog_keyboard
    )
    await query.answer()


async def back_to_catalog_action_menu(query: CallbackQuery, state: FSMContext):
    await state.clear()
    buttons = [
        [
            InlineKeyboardButton(text="Не менять имени каталога", callback_data="show_catalogs_list"),
            InlineKeyboardButton(text="Изменить имя каталога", callback_data="show_catalogs_list_to_rename")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await state.set_state(UpdateProductStates.choose_catalog_action)
    await query.message.answer(text="Выберите действие:", reply_markup=kb)
    await query.answer() 

async def back_to_catalogs_list(query: CallbackQuery, state: FSMContext):
    await state.clear()

    async for db in get_db():
        catalogs = await get_all(db, Catalog)
        kb = create_keyboard(catalogs, "Назад", "back_to_choose_catalog_action")

    await state.set_state(UpdateProductStates.choose_catalog)
    await query.message.answer(
        text="Выберите каталог:",
        reply_markup=kb
    )
    await query.answer()


# Выбор каталога для изменения названия
async def choose_catalog_to_rename(query: CallbackQuery, state: FSMContext):
    data = query.data

    if data == "back_to_choose_catalog_action":
        await state.set_state(UpdateProductStates.back_choose_catalog_action)
        await back_to_catalog_action_menu(query, state)
        return
    

    else:
        catalog_id = int(data)
        await state.update_data(catalog_id=catalog_id)
        await state.set_state(UpdateProductStates.entering_catalog_new_name)
        await query.message.answer(
            text="Введит новое название каталога:",
        )
        await query.answer()

# Ввод названия нового каталога
async def enter_catalog_new_name(mes: Message, state: FSMContext):
    await state.update_data(catalog_new_name=mes.text)
    data = await state.get_data()

    catalog_id = data["catalog_id"]
    async for db in get_db():
        catalog = await db.get(Catalog, catalog_id)

    old_name = catalog.name if catalog else "(не найдено)"
    new_name = mes.text

    buttons = [
        [
            InlineKeyboardButton(text="Да, переименовать", callback_data="confirm_rename_catalog"),
            InlineKeyboardButton(text="Нет, отменить", callback_data="cancel_rename_catalog")
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await state.set_state(UpdateProductStates.confirming_catalog_rename)
    await mes.answer(
        text=f"Переименовать каталог\n<b>{old_name}</b> → <b>{new_name}</b>?",
        reply_markup=kb
    )

# Подтверждение обновления каталога
async def confirm_catalog_new_name(query: CallbackQuery, state: FSMContext):
    query_data = query.data
    data = await state.get_data()

    if query_data == "confirm_rename_catalog":
        catalog_id = data["catalog_id"]
        catalog_new_name = data["catalog_new_name"]
        async for db in get_db():
            catalog = await update_object(db, Catalog, obj_id=catalog_id, name=catalog_new_name)

        await query.message.answer(
            text=f"✅ Каталог успешно переименован на <b>{catalog_new_name}</b>!"
        )
        await asyncio.sleep(0.3)
        await state.clear()
        await state.set_state(UpdateProductStates.choose_catalog_action)
        await choose_catalog_to_step_or_to_rename(query, state)
        await query.answer(text="Обновлено ✅")
    
    elif query_data == "cancel_rename_catalog":
        await state.clear()
        await query.message.answer("Переименование отменено.")
        await asyncio.sleep(0.3)

        await state.set_state(UpdateProductStates.choose_catalog_action)
        await choose_catalog_to_step_or_to_rename(query, state)
        await query.answer()

# Переход от выбора каталога к выбору категории -> выбор действия над категориями
async def road_catalog_to_category(query: CallbackQuery, state: FSMContext):
    data = query.data
    
    if data == "back_to_choose_catalog_action":
        await state.set_state(UpdateProductStates.back_choose_catalog_action)
        await back_to_catalog_action_menu(query, state)
        return
    

    else:
        catalog_id = int(data)
        await state.update_data(catalog_id=catalog_id)
        
        buttons = [
            [
                InlineKeyboardButton(text="Без изменения названия", callback_data="show_categories_list"),
                InlineKeyboardButton(text="Изменить название", callback_data="show_categories_list_to_rename")
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_to_choose_catalog")
            ]
        ]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)

        await state.set_state(UpdateProductStates.choose_category_action)
        await query.message.answer(
            text="Выберите действие над категориями:",
            reply_markup=kb
        )
        await query.answer()
    

# Гойда гойда
# Разпределение действий над категориями
async def choose_category_action(query: CallbackQuery, state: FSMContext):
    data_query = query.data

    if data_query == "back_to_choose_catalog":
        await state.set_state(UpdateProductStates.back_choose_catalog)
        await back_to_catalogs_list(query, state)
        return
    
    data = await state.get_data()
    async for db in get_db():
        categories = await get_categories_by_catalog(db, data["catalog_id"])

    kb = create_keyboard(categories, "Назад", "return_to_choose_category_action")

    if data_query == "show_categories_list":
        await state.set_state(UpdateProductStates.choose_category)
        await query.message.answer(
            text="Выберите категорию:",
            reply_markup=kb
        )
        await query.answer()

    elif data_query == "show_categories_list_to_rename":
        await state.set_state(UpdateProductStates.choose_category_to_rename)
        await query.message.answer(
            text="Выберите категорию, название которой будет изменено:",
            reply_markup=kb
        )
        await query.answer()

async def back_to_category_action_menu(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    catalog_id = data.get("catalog_id")
    state.clear()

    await state.update_data(catalog_id=catalog_id)
        
    buttons = [
        [
            InlineKeyboardButton(text="Без изменения названия", callback_data="show_categories_list"),
            InlineKeyboardButton(text="Изменить название", callback_data="show_categories_list_to_rename")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_choose_catalog")
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await state.set_state(UpdateProductStates.choose_category_action)
    await query.message.answer(
        text="Выберите действие над категориями:",
        reply_markup=kb
    )
    await query.answer()



# Выбор категории для изменения названия
async def choose_category_to_rename(query: CallbackQuery, state: FSMContext):
    data = query.data

    if data == "return_to_choose_category_action":
        await state.set_state(UpdateProductStates.back_choose_category_action)
        await back_to_category_action_menu(query, state)
        return

    else:
        category_id = int(data)
        await state.update_data(category_id=category_id)
        await state.set_state(UpdateProductStates.entering_category_new_name)
        await query.message.answer(
            text="Введите новое название категории:",
        )
        await query.answer()


# Ввод нового названия категории
async def enter_category_new_name(mes: Message, state: FSMContext):
    new_name = mes.text
    await state.update_data(category_new_name=new_name)
    data = await state.get_data()

    async for db in get_db():
        category = await db.get(Category, data["category_id"])

    old_name = category.name if category else "Не найдено"

    buttons = [
        [
            InlineKeyboardButton(text="Да, переименовать", callback_data="confirm_rename_category"),
            InlineKeyboardButton(text="Нет, отменить", callback_data="cancel_rename_category")
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await state.set_state(UpdateProductStates.confirming_category_rename)
    await mes.answer(
        text=f"Переименовать каталог\n<b>{old_name}</b> → <b>{new_name}</b>?",
        reply_markup=kb
    )

# Меню после подтверждения изменения 
async def show_category_action_menu(query, state):
    data = await state.get_data()
    catalog_id = data.get("catalog_id")
    if not catalog_id:
        await query.message.answer("catalog_id не найден в состоянии")
        return

    buttons = [
        [
            InlineKeyboardButton(text="Без изменения названия", callback_data="show_categories_list"),
            InlineKeyboardButton(text="Изменить название", callback_data="show_categories_list_to_rename")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_choose_catalog")
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await state.set_state(UpdateProductStates.choose_category_action)
    await query.message.answer(
        text="Выберите действие над категориями:",
        reply_markup=kb
    )
    await query.answer()


# Подтверждение изменения категории
async def confirm_category_new_name(query: CallbackQuery, state: FSMContext):
    data_query = query.data
    data = await state.get_data()

    if data_query == "confirm_rename_category":
        category_id = data["category_id"]
        catagory_name = data["category_new_name"]
        async for db in get_db():
            category = await update_object(db, Category, category_id, name=catagory_name)
        
        await query.message.answer(
            text=f"✅ Категория успешно переименована на <b>{catagory_name}</b>!"
        )
        await asyncio.sleep(0.3)

        await state.clear()
        await state.update_data(catalog_id=data["catalog_id"])
        await state.set_state(UpdateProductStates.choose_category_action)
        await show_category_action_menu(query, state)
        await query.answer(text="Обновлено ✅")        
        

    elif data_query == "cancel_rename_category":
        await state.clear()
        await state.update_data(catalog_id=data["catalog_id"])
        await query.message.answer("Переименование отменено.")
        await asyncio.sleep(0.3)
        
        await state.set_state(UpdateProductStates.choose_category_action)
        await show_category_action_menu(query, state)
        await query.answer()



def register_update_catalog_and_category_handlers(dp: Dispatcher):
    dp.callback_query.register(choose_catalog_to_step_or_to_rename, F.data == "update_category", IsAdmin())
    dp.callback_query.register(show_catalogs_for_choose_action, UpdateProductStates.choose_catalog_action, IsAdmin())
    dp.callback_query.register(choose_catalog_to_rename, UpdateProductStates.choose_catalog_to_rename, IsAdmin())
    dp.message.register(enter_catalog_new_name, UpdateProductStates.entering_catalog_new_name, IsAdmin())
    dp.callback_query.register(confirm_catalog_new_name, UpdateProductStates.confirming_catalog_rename, IsAdmin())
    dp.callback_query.register(road_catalog_to_category, UpdateProductStates.choose_catalog, IsAdmin())
    dp.callback_query.register(choose_category_action, UpdateProductStates.choose_category_action, IsAdmin())
    dp.callback_query.register(choose_category_to_rename, UpdateProductStates.choose_category_to_rename, IsAdmin())
    dp.message.register(enter_category_new_name, UpdateProductStates.entering_category_new_name, IsAdmin())
    dp.callback_query.register(confirm_category_new_name, UpdateProductStates.confirming_category_rename, IsAdmin())
    dp.callback_query.register(show_category_action_menu, UpdateProductStates.choose_category_action, IsAdmin())
    # dp.callback_query.register(back_to_main_menu, UpdateProductStates.back_to_main_menu, IsAdmin())
    # dp.callback_query.register(back_to_catalog_action_menu, UpdateProductStates.back_choose_catalog_action, IsAdmin())
    # dp.callback_query.register(back_to_catalogs_list, UpdateProductStates.bac)





'''
Не рабочие кнопки назад:
1)Выбор действия над каталогом -> не изменять имя -> назад
2)Выбор действия над каталогом -> не изменять имя -> каталог -> назад
3)Выбор действия над каталогом -> не изменять имя -> каталог -> выбор действия над категорией (не изменять)-> назад
4)Выбор действия над каталогом -> не изменять имя -> каталог -> выбор действия над категорией (изменить)-> назад
5)Выбор действия над каталогом -> не изменять имя -> каталог -> выбор действия над категорией (изменить)-> категория -> отсутствие кнопки назад на этапе ввода
6)Выбор действия над каталогом -> изменить имя -> каталог -> отсутствие кнопки назад на этапе ввода
'''

















































































# # 1. Выбор каталога для углубления или кнопка "Изменить название каталога"
# async def choose_catalog_or_button_to_update(query: CallbackQuery, state: FSMContext):
#     async for db in get_db():
#         catalogs = await get_all(db, Catalog)

#     kb = create_keyboard(catalogs, "Изменить название каталога", "update_catalog_name")
#     await state.set_state(UpdateProductStates.choosing_catalog)
#     await query.message.answer(
#         text="Выберите каталог или измените его название:",
#         reply_markup=kb
#     )
#     await query.answer()

# # 2. Выбор каталога для изменения названия
# # Если нажать кнопку "Изменить название каталога", то всё окей. 
# # Если нажать кнопку с названием каталога, то выводится меню для изменения названия каталога, 
# # а нужно отобразить набор категорий
# # ДОДЕЛАТЬ
# async def choose_catalog_to_rename(query: CallbackQuery, state: FSMContext):
#     data = query.data
#     if data == "update_catalog_name":
#         async for db in get_db():
#             catalogs = await get_all(db, Catalog)

#         kb = create_keyboard(catalogs, "Назад(НЕ РАБОТАЕТ)", "back_to_menu_choose_catalog")
#         await state.set_state(UpdateProductStates.choosing_catalog_to_rename)
#         await query.message.answer(
#             text="Выберите каталог, который хотите переимновать",
#             reply_markup=kb
#         )
#         await query.answer()
    
#     # пока почему-то не работает
#     # не работает, потому что нужно использовать в другом хендлере, 
#     # обрабатывающим UpdateProductStates.choosing_catalog_to_rename 
#     # elif data == "back_to_menu_choose_catalog":
#     #     # Здесь вернуться к начальному состоянию выбора каталога
#     #     await choose_catalog_or_button_to_update(query, state)
#     #     await query.answer()

#     else:
#         # отобразить список категорий этого каталога
#         catalog_id = int(data)
#         await state.update_data(catalog_id=catalog_id)

#         async for db in get_db():
#             categories = await get_categories_by_catalog(db, catalog_id=catalog_id)

#         kb = create_keyboard(categories, "Изменить название категории", "update_category_name")

#         await state.set_state(UpdateProductStates.choosing_category)
#         await query.message.answer(
#             text="Выберите категорию или измените её название:",
#             reply_markup=kb
#         )
#         await query.answer()


# # 3. Ввод нового названия каталога
# async def enter_new_catalog_name(mes: Message, state: FSMContext):
    

#     pass

# 4. Выбор категории для углубления или кнопка "Изменить название категории"

# 5. Выбор категории для изменения названия

# 6. Ввод нового названия категории

# 7. Выбор товара для изменения

# 8. Выбор характеристики для изменения

# 9. Ввод нового значения выбранной характеристики

# 10. <Промежуточно> Подтверждение обновления 










# def register_update_product_handlers(dp: Dispatcher):#
#     dp.callback_query.register(choose_catalog_or_button_to_update, F.data=="update_category", IsAdmin())
#     dp.callback_query.register(choose_catalog_to_rename, UpdateProductStates.choosing_catalog, IsAdmin())