from database.models import Product, Category, Catalog, Unit
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def get_categories_by_catalog(db: AsyncSession, catalog_id: int):
    res = await db.execute(
        select(Category).where(Category.catalog_id == catalog_id)
    )
    return res.scalars().all()


async def get_product_display_data(
        db: AsyncSession,
        catalog_id: int, 
        category_id: int, 
        unit_id: int
) -> dict:
    catalog = await db.get(Catalog, catalog_id)
    category = await db.get(Category, category_id)
    unit = await db.get(Unit, unit_id)

    return {
        "catalog_name": catalog.name if catalog else "–",
        "category_name": category.name if category else "–",
        "unit_name": unit.name if unit else "–",
    }


async def get_product_display_info(db: AsyncSession, product: Product) -> dict:
    category = await db.get(Category, product.category_id)
    catalog = await db.get(Catalog, category.catalog_id) if category else None
    unit = await db.get(Unit, product.unit_id)

    return {
        "catalog": catalog.name if catalog else "-",
        "category": category.name if category else "-",
        "unit": unit.name if unit else "-"
    }