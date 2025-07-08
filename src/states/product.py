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


class UpdateProductStates(StatesGroup):
    back_to_main_menu = State()
    # 1. Для каталога
    choose_catalog_action = State()
    choose_catalog = State()
    choose_catalog_to_rename = State()
    entering_catalog_new_name = State()
    confirming_catalog_rename = State()
    # 1.1 Кнопки назад для каталога
    back_choose_catalog_action = State()
    back_choose_catalog = State()
    back_choose_catalog_to_rename = State()
    back_entering_catalog_new_name = State()
    back_confirming_catalog_rename = State()

    # 2. Для категории
    choose_category_action = State()
    choose_category = State()
    choose_category_to_rename = State()
    entering_category_new_name = State()
    confirming_category_rename = State()
    # 2.1 Кнопки назад для категории
    back_choose_category_action = State()
    back_choose_category = State()
    back_choose_category_to_rename = State()
    back_entering_category_new_name = State()
    back_confirming_category_rename = State()

    # 3. Чёта с товарами делать, подумать нужно


# class UpdateProductStates(StatesGroup):
#     choosing_catalog = State()            # 1. Выбор каталога
#     choosing_catalog_to_rename = State()  # 2. Выбор каталога для переименования
#     entering_catalog_new_name = State()   # 3. Ввод нового имени каталога

#     choosing_category = State()           # 4. Выбор категории
#     choosing_category_to_rename = State() # 5. Выбор категории для переименования
#     entering_category_new_name = State()  # 6. Ввод нового имени категории

#     choosing_product = State()            # 7. Выбор товара
#     choosing_product_field = State()      # 8. Выбор характеристики для изменения
#     entering_product_new_value = State()  # 9. Ввод нового значения
#     # ... 
#     confirming_update = State()           # 10. Подтверждение изменений