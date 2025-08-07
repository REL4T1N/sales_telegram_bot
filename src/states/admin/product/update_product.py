from aiogram.fsm.state import State, StatesGroup

class UpdateProduct(StatesGroup):
    choosing_catalog_action = State()
    choosing_catalog_for_category = State()
    choosing_catalog_rename = State()
    entering_catalog_rename = State()
    confirming_catalog_rename = State()

    choosing_category_action = State()
    choosing_category_for_blocks = State()
    choosing_category_rename = State()
    entering_category_rename = State()
    confirming_category_rename = State()

    # С v1 версии
    choosing_product = State()
    choosing_product_parametr = State()
    entering_new_size = State()
    choosing_new_unit = State()
    entering_new_unit = State()
    confirming_new_unit = State()
    entering_new_count = State()
    entering_new_price = State()
    confirming_product_edit = State()
    choosing_param_edit_action = State()
