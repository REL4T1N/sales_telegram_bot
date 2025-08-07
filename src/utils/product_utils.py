from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Product, Unit
from database.database import get_db

from services.product.base import get_product_display_info

from utils.formatting_float_nums import pretty_edit



async def generate_product_info_text(db: AsyncSession, product: Product, data: dict = None) -> tuple[str, bool]:
    """
    Генерирует текст с информацией о продукте, учитывая возможные новые значения.
    
    Args:
        db: Асинхронная сессия базы данных
        product: Объект продукта
        data: Данные состояния, содержащие новые значения (опционально)
    
    Returns:
        Текст с информацией о продукте в формате HTML
    """
    names = await get_product_display_info(db, product)
    data = data or {}  # Если data не передан, используем пустой словарь
    
    if data.get("new_size") is not None or data.get("new_count") is not None or data.get("new_price") is not None or data.get("new_unit_id") is not None:
        flag = True
    else:
        flag = False

    size_str = pretty_edit(product.size, data.get("new_size"))
    count_str = pretty_edit(product.count, data.get("new_count"), " шт.")
    price_str = pretty_edit(product.price, data.get("new_price"), "₽")

    async for db in get_db():
        new_unit = await db.get(Unit, data.get("new_unit_id"))

    new_unit_name = new_unit.name if new_unit else None
    unit_str = pretty_edit(names["unit"], new_unit_name)

    
    text = (
        f"<b>Информация по продукту:</b>\n"
        f"<b>Каталог:</b> {names['catalog']}\n"
        f"<b>Категория:</b> {names['category']}\n"
        f"<b>Размер единицы продукции:</b> {size_str}\n"
        f"<b>Единица измерения:</b> {unit_str}\n"
        f"<b>Количество продукции:</b> {count_str}\n"
        f"<b>Цена:</b> {price_str}\n"
        f"<b>------</b>\n"
        f"<b>Выберите параметр для изменения:</b>"
    )
    return text, flag
