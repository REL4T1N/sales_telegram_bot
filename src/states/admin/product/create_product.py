from aiogram.fsm.state import State, StatesGroup


class CreateProduct(StatesGroup):

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

    confirming = State()