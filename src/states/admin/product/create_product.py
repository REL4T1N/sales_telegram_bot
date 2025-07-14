from aiogram.fsm.state import State, StatesGroup


class CreateProduct(StatesGroup):
    '''
    1. Меню выбора действия + кнопка назад -> нажали "Добавить товар"
    2. Меню выбора доступных каталогов и inline кнопка "Добавить новый вариант" + кнопка назад ->
        1. Выбрали доступный
    
    '''
    choosing_catalog = State()
    entering_catalog_name = State()
    confirming_catalog_name = State()

    choosing_category = State()
    entering_category_name = State()
    confirming_category_name = State()

    entering_size = State()

    choosing_unit = State()
    entering_new_unit = State()
    confirming_new_unit = State()

    entering_count = State()

    entering_price = State()

    adding_desc = State()
    entering_description = State()

    adding_photo = State()
    sending_photo = State()

    confirming = State()