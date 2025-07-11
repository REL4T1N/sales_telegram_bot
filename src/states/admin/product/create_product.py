from aiogram.fsm.state import State, StatesGroup


class CreateProduct(StatesGroup):
    '''
    1. Меню выбора действия + кнопка назад -> нажали "Добавить товар"
    2. Меню выбора доступных каталогов и inline кнопка "Добавить новый вариант" + кнопка назад ->
        1. Выбрали доступный
    
    '''
    # пробник
    choosing_catalog = State()
    entering_catalog_name = State()
    confirming_catalog_name = State()

    choosing_category = State()
    entering_category_name = State()
    confirming_category_name = State()
    pass