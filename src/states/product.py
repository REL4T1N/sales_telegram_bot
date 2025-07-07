from aiogram.fsm.state import State, StatesGroup


class AddProductStates(StatesGroup):
    choosing_catalog = State()
    entering_catalog = State()
    choosing_category = State()
    entering_category = State()
    entering_size = State()
    choosing_unit = State()
    entering_unit = State()
    entering_quantity = State()
    entering_price = State()
    confirming = State()
    