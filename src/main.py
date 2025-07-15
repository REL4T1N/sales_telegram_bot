import asyncio

from bot.bot import bot
from bot.dispatcher import dp

from handlers.admin.product.create.catalog import admin_create_catalog
from handlers.admin.product.create.category import admin_create_category
from handlers.admin.product.create.enter_params import admin_create_product
from handlers.admin.product.create.unit import admin_create_unit


async def main():
    dp.include_router(admin_create_catalog)
    dp.include_router(admin_create_category)
    dp.include_router(admin_create_unit)
    dp.include_router(admin_create_product)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())