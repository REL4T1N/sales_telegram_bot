from aiogram.fsm.state import State, StatesGroup

class UpdateProduct(StatesGroup):
    choosing_catalog_action = State()
    choosing_catalog_for_category = State()
    choosing_catalog_rename = State()
    entering_catalog_rename = State()
    confirming_catalog_rename = State()

    choosing_category_action = State()
    choosing_category_for_size = State()
    choosing_category_rename = State()
    entering_category_rename = State()
    confirming_category_rename = State()

    entering_new_size = State()

    choosing_unit_action = State()
    
